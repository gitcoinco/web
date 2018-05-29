require "eth"
require "json"

workdir = Dir.pwd

Dir.each_child("erc20") do |file|
  next if file == "$template.json" || !file.end_with?("json")
  puts "processing file:#{file}"
  fullpath = "#{workdir}/erc20/#{file}"
  begin
    json = JSON.parse IO.read(fullpath)
  rescue => e
    puts e.message
    exit false
  end
  address_text = json["address"]
  downcase_address = address_text.downcase
  checksum_address = Eth::Utils.format_address address_text

  if address_text != checksum_address
    puts "rewrite file:#{file}"
    json["address"] = checksum_address
    File.open(fullpath, 'w') {|f| f.write JSON.pretty_generate(json, indent: " "*4) }
  end

  img = "#{workdir}/images/#{downcase_address}.png"
  if File.exists?(img)
    puts "rewrite image:#{file}"
    File.rename(img, "#{workdir}/images/#{checksum_address}.png")
  end
end
