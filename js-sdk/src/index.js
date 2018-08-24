// Import stylesheets
import './style.css';
import Siema from 'siema';

class Widget {
  constructor(options = {}) {
    this.options = options;
    this.el = this.options.el || document.querySelector(options.selector || '.gitcoin-widget');
    this.options.organization = this.el.dataset.organization || this.options.organization;
    this.options.repository = this.el.dataset.repository || this.options.repository;
    this.options.orderBy = this.el.dataset['order-by'] || this.options.orderBy;
    this.options.limit = this.el.dataset['limit'] || this.options.limit;
    fetch(`https://gitcoin.co/api/v0.1/bounties/?raw_data=${this.options.repository}&org=${this.options.organization}&network=mainnet&coinbase=unknown&order_by=${this.orderBy()}&limit=${this.limit()}`)
      .then(response => response.json())
      .then(json => {
        this.data = json;
        this.render();
      });
  }
  orderBy() {
    return this.options.orderBy ? this.options.orderBy : '-expires_date';
  }
  limit() {
    return this.options.limit ? this.options.limit : '20';
  }
  static logo() {
    const anchor = document.createElement('a');

    anchor.target = '_blank';
    anchor.href = 'https://gitcoin.co';
    const logo = document.createElement('img');

    anchor.appendChild(logo);
    // need a srcset or svg logo for responsiveness
    logo.src = 'https://s.gitcoin.co/static/v2/images/logo.png';
    logo.className = 'gitcoin-widget__logo';
    return anchor;
  }

  static top() {
    const top = document.createElement('div');

    top.className = 'gitcoin-widget__top';
    top.appendChild(Widget.logo());
    const slogan = document.createElement('span');

    slogan.style.fontSize = '11px';
    slogan.innerHTML = 'Grow open source!';
    top.appendChild(slogan);
    return top;
  }

  static bountyRow(bounties) {
    const row = document.createElement('div');

    row.className = 'gitcoin-widget__bounty-row';
    for (let i = 0; i < bounties.length; i++) {
      row.appendChild(Widget.bounty(bounties[i]));
    }
    return row;
  }

  static formatExpiresIn(to) {
    const from = new Date();
    const diff = Math.floor(to - from);
    const day = 1000 * 60 * 60 * 24;
    const days = Math.floor(diff / day);
    const months = Math.floor(days / 31);
    let message;

    if (months < 0 && days < 0) {
      message = 'Expired';
    } else if (months === 0) {
      message = `Expires In ${days} Day${days > 0 ? 's' : ''}`;
    } else {
      message = `Expires In ${months} Month${months > 0 ? 's' : ''}`;
    }
    return message;
  }

  static bounty(b) {
    const bounty = document.createElement('div');

    bounty.className = 'gitcoin-widget__bounty';
    const anchor = document.createElement('a');

    anchor.target = '_blank';
    anchor.href = b.url;
    const title = document.createElement('h1');

    title.innerHTML = b.title;
    anchor.appendChild(title);
    bounty.appendChild(anchor);
    const expires = document.createElement('div');

    expires.className = 'gitcoin-widget__expires';
    const expiresIn = new Date(b.expires_date);

    expires.innerHTML = Widget.formatExpiresIn(expiresIn);
    bounty.appendChild(expires);
    const labels = document.createElement('div');

    labels.className = 'gitcoin-widget__labels';
    labels.innerHTML = `<div class="gitcoin-widget__label gitcoin-widget__label--eth">${b.value_true} ${b.token_name}</div><div class="gitcoin-widget__label gitcoin-widget__label--usd">${b.value_in_usdt} USD</div>`;
    bounty.appendChild(labels);
    return bounty;
  }

  bottom() {
    const bottom = document.createElement('div');

    bottom.className = 'gitcoin-widget__bottom';
    bottom.appendChild(this.left());
    bottom.appendChild(this.right());
    return bottom;
  }

  left() {
    const left = document.createElement('div');

    left.className = 'gitcoin-widget__left';
    const avatar = document.createElement('img');

    avatar.className = 'gitcoin-widget__avatar';
    avatar.src = `https://github.com/${this.options.organization}.png`;
    left.appendChild(avatar);
    const title = document.createElement('h1');

    title.innerHTML = `${this.options.organization} <br />supports funded issues`;
    left.appendChild(title);
    const div = document.createElement('div');

    div.style.fontSize = '11px';
    div.innerHTML = 'Browse issues at: <a href="https://gitcoin.co/explorer" title="Gitcoin Explorer">https://gitcoin.co/explorer</a>';
    div.style.color = 'rgb(102, 102, 102)';
    left.appendChild(div);
    return left;
  }

  formattedTotals() {
    let totals = [ 0, 0 ];
    let i = this.data.length;

    while (i--) {
      totals[0] += parseFloat(this.data[i].value_true);
      totals[1] += parseFloat(this.data[i].value_in_usdt);
    }
    return `Total: ${this.data.length} issues / ${Math.round(totals[0] * 100) / 100} ETH / ${Math.round(totals[1] * 100) / 100} USD`;
  }

  right() {
    const right = document.createElement('div');

    right.className = 'gitcoin-widget__right';
    const bar = document.createElement('div');

    bar.className = 'gitcoin-widget__bar';
    bar.innerHTML = 'Recently Funded Issues:';
    const total = document.createElement('span');
    const totalValueEth = this.data.reduce((a, b) => a.value_in_eth + b.value_in_eth, 0);

    total.innerHTML = this.formattedTotals();
    bar.appendChild(total);
    right.appendChild(bar);
    const slider = document.createElement('div');

    function groupBounties(arr, n, fn) {
      for (var i = 0; i < arr.length; i += n) {
        fn(arr.slice(i, i + n));
      }
    }
    
    slider.className = 'siema';

    groupBounties(this.data, 4, function(group) {
      const slide = document.createElement('div');

      slide.appendChild(Widget.bountyRow(group));
      slider.appendChild(slide);
    });

    right.appendChild(slider);
    return right;
  }

  fragment() {
    const divs = [
      Widget.top(), this.bottom()
    ];
    const fragment = document.createDocumentFragment();

    for (let i = 0; i < divs.length; i++) {
      fragment.appendChild(divs[i]);
    }
    return fragment;
  }
  render() {
    this.el.appendChild(this.fragment());
    const s = new Siema({
      loop: true
    });

    // Because
    s.resizeHandler();
    setInterval(() => s.next(), 10000);
  }
}

// Auto
if (document.querySelector('.gitcoin-widget')) {
  const found = document.querySelectorAll('.gitcoin-widget');
  const createWidget = options => new Widget(options);

  for (let i = 0; i < found.length; i++) {
    createWidget({ el: found[i]});
  }
}

export { Widget };
