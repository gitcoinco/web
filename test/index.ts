import * as fs from 'fs'
import * as pngjs from 'pngjs'
import chalk from 'chalk'


const dateExp = /^\d{4}-\d{2}(-\d{2})?$/

const urlExp = /^(?:([A-Za-z]+):)?(\/{0,3})([0-9.\-A-Za-z]+)(?::(\d+))?(?:\/([^?#]*))?(?:\?([^#]*))?(?:#(.*))?$/

const emailExp = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/

const jsonExp = /\.json$/

const imgExp = /\.png$/

const ethAddressExp = /^(0x)?[0-9a-f]{40}$/i

const isEthAddress = address => ethAddressExp.test(address)

const isEosToken = (account: string) => {
  return !!account && account.search(/^[a-z1-5.]{1,11}[a-z1-5]$/) === 0
}

const isEthAddressJson = (filename) => jsonExp.test(filename) && isEthAddress(filename.replace(jsonExp, ''))

const isEosSymbolAndAccountName = (filenameWithoutExt) => {
  if (filenameWithoutExt.indexOf('@') === -1) {
    return false
  }
  const arr = filenameWithoutExt.split('@')
  const accountName = arr[1]

  return isEosToken(accountName)
}

const isEosTokenJson = (filename) => {
  if (!jsonExp.test(filename)) {
    return false
  }
  const filenameWithoutExt = filename.replace(jsonExp, '')
  return isEosSymbolAndAccountName(filenameWithoutExt)
}

const isEthAddressPng = (filename) => imgExp.test(filename) && isEthAddress(filename.replace(imgExp, ''))

const isEosTokenPng = (filename) => {
  if (!imgExp.test(filename)) {
    return false
  }
  const filenameWithoutExt = filename.replace(imgExp, '')
  return isEosSymbolAndAccountName(filenameWithoutExt)
}

const isStringWithCharacter = (str) => {
  return str && typeof str === 'string' && str.trim()
}

const isUrl = (url) => isStringWithCharacter(url) && url.match(urlExp)

const exitWithMsg = (msg) => {
  console.log(chalk.red(msg))
  process.exit(1)
}

const notice = (msg) => {
  console.log(chalk.yellow(msg))
}

const commonFieldCheck = (jsonFileName, obj) => {
  if (!obj.symbol) {
    exitWithMsg(`ERROR! json file ${jsonFileName} content must have symbol field`)
  }

  if (obj.published_on !== undefined) {
    if (obj.published_on.search(dateExp) === -1) {
      exitWithMsg(`ERROR! json file ${jsonFileName}'s published_on field ${obj.published_on} must be format of YYYY-MM-DD or YYYY-MM-DD`)
    }
  }

  if (obj.email !== undefined) {
    if (obj.email.search(emailExp) === -1) {
      exitWithMsg(`ERROR! json file ${jsonFileName}'s email field ${obj.email} must be an email`)
    }
  }

  if (obj.overview !== undefined) {
    if (!Object.keys(obj.overview).every(k => !!isStringWithCharacter(obj.overview[k]))) {
      exitWithMsg(`ERROR! json file ${jsonFileName}'s overview field must be a string (not empty)`)
    }
  }

  if (obj.links !== undefined) {
    if (!Object.keys(obj.links).every(k => isUrl(obj.links[k]))) {
      exitWithMsg(`ERROR! json file ${jsonFileName}'s links every field must be an url`)
    }
  }

  if (obj.state !== undefined) {
    if (!['LOCKED', 'NORMAL'].includes(obj.state)) {
      exitWithMsg(`ERROR! json file ${jsonFileName}'s state field ${obj.state} must be 'LOCKED' or 'NORMAL'`)
    }
  }

  if (obj.initial_price !== undefined) {
    const keys = Object.keys(obj.initial_price)
    if (keys.some(k => !['BTC', 'ETH', 'USD', 'EOS'].includes(k))) {
      exitWithMsg(`ERROR! json file ${jsonFileName}'s initial_price field ${JSON.stringify(obj.initial_price)} only support BTC ETH USD EOS`)
    }

    keys.forEach(k => {
      if (!obj.initial_price[k].endsWith(` ${k}`)) {
        exitWithMsg(`ERROR! json file ${jsonFileName}'s initial_price field ${obj.initial_price[k]} must end with ${'space+' + k}, just see example`)
      }
    })
  }

  ['website', 'whitepaper'].forEach(k => {
    if (obj[k] !== undefined) {
      if (!isUrl(obj[k])) {
        exitWithMsg(`ERROR! json file ${jsonFileName}'s ${k} field ${obj[k]} must an url`)
      }
    }
  })
}

const getObjIfNoError = (jsonFileName, type) => {
  const addr = jsonFileName.replace(jsonExp, '')
  let prepath = ''
  let parseErr = null

  if (type === 'ETHEREUM') {
    prepath = './erc20/'

    if (!isEthAddress(addr)) {
      exitWithMsg(`ERROR! json file name ${jsonFileName} is not like a ${type} address.json`)
    }
  } else if (type === 'EOS') {
    prepath = './eos-token/'

    if (!isEosSymbolAndAccountName(addr)) {
      exitWithMsg(`ERROR! json file name ${jsonFileName} is not like a ${type} symbol@account_name.json`)
    }
  }

  const content = fs.readFileSync(`${prepath}${addr}.json`).toString()

  if (content.indexOf('�') !== -1) {
    exitWithMsg(`ERROR! json file name ${jsonFileName} must be utf-8 encoding`)
  }

  try {
    return JSON.parse(content)
  } catch (e) {
    parseErr = e
  }

  if (parseErr) {
    exitWithMsg(`ERROR! json file name ${jsonFileName} parse error, please check first (maybe has some unnecessary space or comma symbol like ",")`)
  }
}

const jsonFileNames = fs.readdirSync('./erc20')
const eosJsonFileNames = fs.readdirSync('./eos-token')
const imageFileNames = fs.readdirSync('./images')

const jsonFileCheck = (jsonFileName, type) => {
  const filenameWithoutExt = jsonFileName.replace(jsonExp, '')
  const imageAddrs = type === 'ETHEREUM' ? imageFileNames.map(n => n.slice(0, 42)).filter(n => {
    return n.startsWith('0x')
  }) : imageFileNames.filter(n => !n.startsWith('0x'))

  const lowerCaseImageAddrs =imageAddrs.map(x => x.toLowerCase())
  const obj = getObjIfNoError(jsonFileName, type)

  if (type === 'ETHEREUM') {
    const address = obj.address

    if (!lowerCaseImageAddrs.includes(filenameWithoutExt.toLowerCase())) {
      notice(`Warning! dose not have ${filenameWithoutExt + '.png'} in images dir, please check first`)
    } else if (!imageAddrs.includes(address)) {
      const imgAddr = imageAddrs.find(imgad => {
        return imgad.toLowerCase() === filenameWithoutExt.toLowerCase()
      })
      exitWithMsg(`Warning! ${imgAddr + '.png'} in images dir, that capital and small letter isn't quite the same with ${address}`)
    }

    if (!address) {
      exitWithMsg(`ERROR! json file ${jsonFileName} content must have address field`)
    }
    if (!isEthAddress(address)) {
      exitWithMsg(`ERROR! json file ${jsonFileName} address field must be an ethereum address`)
    }
    if (address.toLowerCase() !== filenameWithoutExt.toLowerCase()) {
      exitWithMsg(`ERROR! json file ${jsonFileName} should be the same with address field ${address}`)
    } else if (address !== filenameWithoutExt) {
      // exitWithMsg(`Warning! json file ${jsonFileName}, that capital and small letter isn't quite the same with object.address ${obj.address}`)
    }
  } else if (type === 'EOS') {
    const account_name = obj.account_name
    const symbol = obj.symbol
    const symbolFromFilename = filenameWithoutExt.split('@')[0]
    const accountNameFromFilename = filenameWithoutExt.split('@')[1]

    if (!lowerCaseImageAddrs.includes(filenameWithoutExt.toLowerCase())) {
      notice(`Warning! dose not have ${filenameWithoutExt + '.png'} in images dir, please check first`)
    } else if (!imageAddrs.includes(filenameWithoutExt)) {
      const imgAddr = imageAddrs.find(imgad => {
        return imgad.toLowerCase() === filenameWithoutExt.toLowerCase()
      })
      exitWithMsg(`Warning! ${imgAddr + '.png'} in images dir, that capital and small letter isn't quite the same with ${filenameWithoutExt}`)
    }

    if (!account_name) {
      exitWithMsg(`ERROR! json file ${jsonFileName} content must have acount_name field`)
    }
    if (!isEosToken(account_name)) {
      exitWithMsg(`ERROR! json file ${jsonFileName} account_name field must be an eos account name`)
    }
    if (symbol.toLowerCase() !== symbolFromFilename.toLowerCase()) {
      exitWithMsg(`ERROR! json file ${jsonFileName} should have same symbol with symbol field ${symbol}`)
    }
    if (account_name.toLowerCase() !== accountNameFromFilename.toLowerCase()) {
      exitWithMsg(`ERROR! json file ${jsonFileName} should have same account_name with account_name field ${account_name}`)
    } else if (account_name !== accountNameFromFilename) {
      // exitWithMsg(`Warning! json file ${jsonFileName}, that capital and small letter isn't quite the same with object.account_name ${obj.address}`)
    }
  }

  commonFieldCheck(jsonFileName, obj)
}

const jsonFileNameFilter = jsonFileName => {
  return jsonFileName !== '$template.json' && jsonFileName.endsWith('.json')
}

jsonFileNames
  .filter(jsonFileNameFilter)
  .forEach(jsonFileName => {
    jsonFileCheck(jsonFileName, 'ETHEREUM')
  })

eosJsonFileNames
  .filter(jsonFileNameFilter)
  .forEach(jsonFileName => {
    jsonFileCheck(jsonFileName, 'EOS')
  })

  

imageFileNames.forEach(n => {
  const path = `./images/${n}`
  
  if (imgExp.test(n)) {
    fs.createReadStream(path)
      .pipe(new pngjs.PNG()).on('metadata', (metadata) => {
        if (metadata.width !== metadata.height) {
          notice(`${n} image width ${metadata.width} !== height ${metadata.height}`)
        }
        // if (metadata.width !== 120 || metadata.height !== 80) {
        //   notice(`${n} image width and height ${metadata.width} must be 80px or 120px`)
        // }
        if (!metadata.alpha) {
          notice(`${n} image must have transparent background`)
        }
      }).on('error', (err) => {
        exitWithMsg(`${n} image parse error ${err.message}`)
      })
  } else {
    notice(`${n} image must be png`)
  }
})

const checkWrongDirectoryItem = (directory, filename) => {
  const errorMsg = `${filename} in the wrong directory ${directory}/`
  if (directory === './erc20') {
    if (['$template.json', 'README.md'].indexOf(filename) === -1 && !isEthAddressJson(filename)) {
      exitWithMsg(errorMsg)
    }

  } else if (directory === './eos-token') {
    if (['$template.json', 'README.md'].indexOf(filename) === -1 && !isEosTokenJson(filename)) {
      exitWithMsg(errorMsg)
    }

  } else if (directory === './images') {
    if (['bitcoin.png', 'eos.png', 'ethereum.png', 'omni_31.png', 'atom.png', 'cosmos.png', 'litecoin.png','tron.png','bitcoincash.png','nervos.png','polkadot.png','westend.png','kusama.png','filecoin.png','tezos.png'].indexOf(filename) === -1 &&
      !isEthAddressPng(filename) &&
      !isEosTokenPng(filename)) {
      // temporality not throw
      if (filename === '0x4488ed050cd13ccfe0b0fcf3d168216830142775.jpg') {
        notice(errorMsg)
      } else {
        exitWithMsg(errorMsg)
      }
    }

  } else if (directory === './tutorial') {
    // do nothing
  } else if (isEthAddressJson(filename) ||
      isEthAddressPng(filename) ||
      isEosTokenJson(filename) ||
      isEosTokenPng(filename)
    ) {
    exitWithMsg(errorMsg)
  }
}

const checkWrongDirectory = (directory) => {
  fs.readdirSync(directory).forEach((filename) => {
    // filter dot files
    if (!filename.startsWith('.')) {
      const path = directory + '/' + filename
      const stats = fs.statSync(path)
      if (stats.isDirectory()) {
        checkWrongDirectory(path)

      } else {
        checkWrongDirectoryItem(directory, filename)
      }
    }
  })
}

checkWrongDirectory('.')
