document.addEventListener('DOMContentLoaded', () => {
  // configure the bubbles
  const SCROLL_SPEED = 0.3;
  const NOISE_SPEED = 0.004;
  const NOISE_AMOUNT = 5;
  const CANVAS_WIDTH = 2800;
  const bubblesEl = document.querySelector('.bubbles');
  const bubbleSpecs = [
    { s: .6, x: 1134, y: 45 },
    { s: .6, x: 1620, y: 271 },
    { s: .6, x: 1761, y: 372 },
    { s: .6, x: 2499, y: 79 },
    { s: .6, x: 2704, y: 334 },
    { s: .6, x: 2271, y: 356 },
    { s: .6, x: 795, y: 226 },
    { s: .6, x: 276, y: 256 },
    { s: .6, x: 1210, y: 365 },
    { s: .6, x: 444, y: 193 },
    { s: .6, x: 2545, y: 387 },
    { s: .8, x: 1303, y: 193 },
    { s: .8, x: 907, y: 88 },
    { s: .8, x: 633, y: 320 },
    { s: .8, x: 323, y: 60 },
    { s: .8, x: 129, y: 357 },
    { s: .8, x: 1440, y: 342 },
    { s: .8, x: 1929, y: 293 },
    { s: .8, x: 2135, y: 198 },
    { s: .8, x: 2276, y: 82 },
    { s: .8, x: 2654, y: 182 },
    { s: .8, x: 2783, y: 60 },
    { x: 1519, y: 118 },
    { x: 1071, y: 233 },
    { x: 1773, y: 148 },
    { x: 2098, y: 385 },
    { x: 2423, y: 244 },
    { x: 901, y: 385 },
    { x: 624, y: 111 },
    { x: 75, y: 103 },
    { x: 413, y: 367 },
    { x: 2895, y: 271 },
    { x: 1990, y: 75 }
  ];

  class Bubbles {
    constructor(specs) {
      this.bubbles = [];

      specs.forEach((spec, index) => {
        this.bubbles.push(new Bubble(index, spec));
      });

      requestAnimationFrame(this.update.bind(this));
      bubblesEl.style.opacity = 1;
    }

    update() {
      this.bubbles.forEach(bubble => bubble.update());
      this.raf = requestAnimationFrame(this.update.bind(this));
    }
  }

  class Bubble {
    constructor(index, {
      x,
      y,
      s = 1
    }) {
      this.index = index;
      this.x = x;
      this.y = y;
      this.scale = s;

      this.noiseSeedX = Math.floor(Math.random() * 64000);
      this.noiseSeedY = Math.floor(Math.random() * 64000);
      this.el = bubblesEl.children[index];
      if (!this.el) {
        return;
      }

      this.el.classList.add(`logo${this.index + 1}`);
    }

    update() {
      if (!this.el) {
        return;
      }
      this.noiseSeedX += NOISE_SPEED;
      this.noiseSeedY += NOISE_SPEED;
      let randomX = noise.simplex2(this.noiseSeedX, 0);
      let randomY = noise.simplex2(this.noiseSeedY, 0);

      this.x -= SCROLL_SPEED;
      this.xWithNoise = this.x + (randomX * NOISE_AMOUNT);
      this.yWithNoise = this.y + (randomY * NOISE_AMOUNT);

      if (this.x < -200) {
        this.x = CANVAS_WIDTH;
      }

      this.el.style.transform = `translate(${this.xWithNoise}px, ${this.yWithNoise}px) scale(${this.scale})`;
    }
  }

  noise.seed(Math.floor(Math.random() * 64000));

  // init the bubbles
  const bubbles = new Bubbles(bubbleSpecs);
});
