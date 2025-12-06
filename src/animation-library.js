/**
 * VidIn Professional Animation Library
 * 13 Pre-built animation sequences for LinkedIn-style videos
 * Built with Anime.js 3.2.2
 */

const VidIn = {};

// Dark color palette for consistent styling
VidIn.DARK_BACKGROUNDS = [
  '#0f0f1a',  // Deep navy
  '#1a1a2e',  // Dark purple-navy
  '#16213e',  // Dark blue
  '#1a1a1a',  // Near black
  '#0d1b2a',  // Dark teal-blue
  '#1b2838',  // Steam dark
  '#2d132c',  // Dark purple
  '#1e3a5f',  // Dark ocean
  '#0a192f',  // Terminal dark
  '#1f1f2e',  // Soft dark
];

VidIn.LIGHT_TEXT = '#ffffff';
VidIn.MUTED_TEXT = 'rgba(255,255,255,0.7)';
VidIn.SUBTLE_TEXT = 'rgba(255,255,255,0.5)';

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

VidIn._createParticles = function(container, count, color, size) {
  size = size || 'random';
  const particles = [];
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    const s = size === 'random' ? 4 + Math.random() * 12 : size;
    p.className = 'vidin-particle';
    p.style.cssText = 'position:absolute;left:' + (Math.random() * 100) + '%;top:' + (Math.random() * 100) + '%;width:' + s + 'px;height:' + s + 'px;background:radial-gradient(circle, ' + color + ', transparent 70%);border-radius:50%;pointer-events:none;opacity:0;';
    container.appendChild(p);
    particles.push(p);
  }
  return particles;
};

VidIn._createGlow = function(container, x, y, size, color, blur) {
  blur = blur || 80;
  const glow = document.createElement('div');
  glow.className = 'vidin-glow';
  glow.style.cssText = 'position:absolute;left:' + x + ';top:' + y + ';width:' + size + 'px;height:' + size + 'px;background:' + color + ';border-radius:50%;filter:blur(' + blur + 'px);pointer-events:none;opacity:0;transform:scale(0.5);';
  container.appendChild(glow);
  return glow;
};

VidIn._createShape = function(container, type, x, y, size, color, rotation) {
  rotation = rotation || 0;
  const shape = document.createElement('div');
  shape.className = 'vidin-shape';
  let styles = 'position:absolute;left:' + x + ';top:' + y + ';width:' + size + 'px;height:' + size + 'px;pointer-events:none;opacity:0;transform:rotate(' + rotation + 'deg) scale(0);';
  
  if (type === 'ring') {
    styles += 'border:3px solid ' + color + ';border-radius:50%;';
  } else if (type === 'square') {
    styles += 'border:3px solid ' + color + ';border-radius:12px;';
  } else if (type === 'dot') {
    styles += 'background:' + color + ';border-radius:50%;';
  }
  
  shape.style.cssText = styles;
  container.appendChild(shape);
  return shape;
};

VidIn._animateParticles = function(particles, delay) {
  particles.forEach(function(p, i) {
    anime({
      targets: p,
      translateX: function() { return anime.random(-60, 60); },
      translateY: function() { return anime.random(-60, 60); },
      duration: function() { return anime.random(4000, 7000); },
      delay: delay + i * 100,
      direction: 'alternate',
      loop: true,
      easing: 'easeInOutSine'
    });
  });
};

// ============================================================================
// 1. HERO TITLE REVEAL
// ============================================================================
VidIn.heroTitleReveal = function(container, opts) {
  const title = opts.title;
  const subtitle = opts.subtitle;
  const icon = opts.icon;
  const primaryColor = opts.primaryColor;
  const secondaryColor = opts.secondaryColor;
  const bgColor = opts.bgColor || '#0f0f1a';

  container.innerHTML = '<div class="vidin-hero" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';">' +
    '<div class="hero-bg-container" style="position:absolute;inset:0;"></div>' +
    '<div class="hero-icon-container" style="position:relative;z-index:10;margin-bottom:40px;">' +
      '<div class="hero-icon-glow" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:200px;height:200px;background:' + primaryColor + ';border-radius:50%;filter:blur(60px);opacity:0;"></div>' +
      '<div class="hero-icon-ring" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:180px;height:180px;border:4px solid ' + primaryColor + '40;border-radius:50%;opacity:0;"></div>' +
      '<i class="' + icon + ' hero-icon" style="font-size:120px;color:' + primaryColor + ';position:relative;z-index:2;opacity:0;text-shadow:0 0 60px ' + primaryColor + ';"></i>' +
    '</div>' +
    '<h1 class="hero-title" style="font-family:Poppins,sans-serif;font-size:clamp(48px,8vw,96px);font-weight:800;color:#fff;text-align:center;margin:0;line-height:1.1;letter-spacing:-3px;opacity:0;text-shadow:0 4px 60px rgba(0,0,0,0.5);max-width:90%;">' + title + '</h1>' +
    '<p class="hero-subtitle" style="font-family:Inter,sans-serif;font-size:clamp(18px,3vw,32px);color:rgba(255,255,255,0.8);margin-top:30px;text-align:center;opacity:0;max-width:80%;">' + subtitle + '</p>' +
    '<div class="hero-line" style="width:0;height:4px;background:linear-gradient(90deg,transparent,' + primaryColor + ',' + secondaryColor + ',transparent);margin-top:40px;border-radius:2px;"></div>' +
  '</div>';

  var bgContainer = container.querySelector('.hero-bg-container');
  
  var glow1 = VidIn._createGlow(bgContainer, '-10%', '-10%', 600, primaryColor + '50', 100);
  var glow2 = VidIn._createGlow(bgContainer, '70%', '60%', 500, secondaryColor + '40', 80);
  var particles = VidIn._createParticles(bgContainer, 20, primaryColor);
  var shape1 = VidIn._createShape(bgContainer, 'ring', '85%', '15%', 100, primaryColor + '60', 15);
  var shape2 = VidIn._createShape(bgContainer, 'square', '10%', '75%', 80, secondaryColor + '50', -10);

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: [glow1, glow2], opacity: [0, 1], scale: [0.5, 1], duration: 2000 }, 0);
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.3, 0.8)]; }, scale: function() { return [0, anime.random(0.8, 1.5)]; }, duration: 1500, delay: anime.stagger(50) }, 200);
  tl.add({ targets: '.hero-icon-glow', opacity: [0, 0.7], scale: [0.3, 1.2], duration: 1000 }, 300);
  tl.add({ targets: '.hero-icon-ring', opacity: [0, 1], scale: [0.5, 1], duration: 800, easing: 'easeOutBack' }, 400);
  tl.add({ targets: '.hero-icon', opacity: [0, 1], translateY: [-80, 0], scale: [0.5, 1], duration: 1000, easing: 'easeOutElastic(1, .5)' }, 500);
  tl.add({ targets: '.hero-title', opacity: [0, 1], translateY: [60, 0], duration: 1200 }, 900);
  tl.add({ targets: '.hero-subtitle', opacity: [0, 1], translateY: [30, 0], duration: 800 }, 1300);
  tl.add({ targets: '.hero-line', width: ['0%', '50%'], duration: 1000 }, 1500);
  tl.add({ targets: [shape1, shape2], opacity: [0, 1], scale: [0, 1], duration: 800, delay: anime.stagger(100), easing: 'easeOutBack' }, 800);

  VidIn._animateParticles(particles, 2000);
  anime({ targets: '.hero-icon', translateY: [-8, 8], duration: 2500, delay: 2000, direction: 'alternate', loop: true, easing: 'easeInOutSine' });

  return tl;
};

// ============================================================================
// 2. STATISTIC SHOWCASE
// ============================================================================
VidIn.statisticShowcase = function(container, opts) {
  var number = opts.number;
  var suffix = opts.suffix || '';
  var label = opts.label;
  var icon = opts.icon;
  var color = opts.color;
  var bgColor = opts.bgColor || '#1a1a2e';

  container.innerHTML = '<div class="vidin-stat" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';">' +
    '<div class="stat-bg-container" style="position:absolute;inset:0;"></div>' +
    '<div class="stat-ring-outer" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:400px;height:400px;border:2px solid ' + color + '20;border-radius:50%;opacity:0;"></div>' +
    '<div class="stat-ring-inner" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:300px;height:300px;border:3px solid ' + color + '40;border-radius:50%;opacity:0;"></div>' +
    '<div class="stat-icon-wrap" style="position:relative;z-index:10;margin-bottom:20px;">' +
      '<i class="' + icon + ' stat-icon" style="font-size:80px;color:' + color + ';opacity:0;filter:drop-shadow(0 0 30px ' + color + ');"></i>' +
    '</div>' +
    '<div class="stat-number-wrap" style="display:flex;align-items:baseline;position:relative;z-index:10;">' +
      '<span class="stat-number" style="font-family:Space Grotesk,sans-serif;font-size:clamp(100px,20vw,200px);font-weight:700;color:#fff;line-height:1;opacity:0;">0</span>' +
      '<span class="stat-suffix" style="font-family:Space Grotesk,sans-serif;font-size:clamp(40px,8vw,80px);font-weight:700;color:' + color + ';margin-left:10px;opacity:0;">' + suffix + '</span>' +
    '</div>' +
    '<p class="stat-label" style="font-family:Inter,sans-serif;font-size:clamp(20px,4vw,36px);color:rgba(255,255,255,0.7);margin-top:20px;text-align:center;opacity:0;letter-spacing:2px;text-transform:uppercase;">' + label + '</p>' +
  '</div>';

  var bgContainer = container.querySelector('.stat-bg-container');
  var glow1 = VidIn._createGlow(bgContainer, '50%', '50%', 500, color + '30', 100);
  glow1.style.transform = 'translate(-50%, -50%) scale(0.5)';
  var particles = VidIn._createParticles(bgContainer, 18, color);

  var counterObj = { value: 0 };
  var numberEl = container.querySelector('.stat-number');

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: glow1, opacity: [0, 1], scale: [0.3, 1.5], duration: 1500 }, 0);
  tl.add({ targets: '.stat-ring-outer', opacity: [0, 1], scale: [0.5, 1], duration: 1200 }, 300);
  tl.add({ targets: '.stat-ring-inner', opacity: [0, 1], scale: [0.3, 1], duration: 1000, easing: 'easeOutBack' }, 500);
  tl.add({ targets: '.stat-icon', opacity: [0, 1], scale: [0, 1.2, 1], duration: 800, easing: 'easeOutElastic(1, .6)' }, 600);
  tl.add({ targets: '.stat-number', opacity: [0, 1], scale: [0.5, 1.1, 1], duration: 600, easing: 'easeOutBack' }, 800);
  tl.add({ targets: counterObj, value: [0, number], round: 1, duration: 1500, easing: 'easeOutExpo', update: function() { numberEl.textContent = Math.round(counterObj.value); } }, 900);
  tl.add({ targets: '.stat-suffix', opacity: [0, 1], translateX: [-30, 0], duration: 600 }, 1400);
  tl.add({ targets: '.stat-label', opacity: [0, 1], translateY: [20, 0], duration: 600 }, 1600);
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.3, 0.7)]; }, scale: function() { return [0, anime.random(0.8, 1.3)]; }, duration: 1000, delay: anime.stagger(40) }, 400);

  VidIn._animateParticles(particles, 2500);
  anime({ targets: ['.stat-ring-outer', '.stat-ring-inner'], scale: [1, 1.05, 1], duration: 2000, delay: 2500, direction: 'alternate', loop: true, easing: 'easeInOutSine' });

  return tl;
};

// ============================================================================
// 3. BEFORE/AFTER COMPARISON
// ============================================================================
VidIn.beforeAfterComparison = function(container, opts) {
  var beforeValue = opts.beforeValue;
  var afterValue = opts.afterValue;
  var unit = opts.unit;
  var label = opts.label;
  var beforeColor = opts.beforeColor || '#EF4444';
  var afterColor = opts.afterColor || '#10B981';
  var bgColor = opts.bgColor || '#1a1a2e';

  var maxValue = Math.max(beforeValue, afterValue);
  var beforeHeight = (beforeValue / maxValue) * 100;
  var afterHeight = (afterValue / maxValue) * 100;
  var reduction = Math.round((1 - afterValue / beforeValue) * 100);

  container.innerHTML = '<div class="vidin-comparison" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';padding:60px;">' +
    '<div class="comp-bg-container" style="position:absolute;inset:0;"></div>' +
    '<h2 class="comp-title" style="font-family:Poppins,sans-serif;font-size:clamp(28px,5vw,48px);font-weight:700;color:#fff;margin-bottom:60px;opacity:0;position:relative;z-index:10;">' + label + '</h2>' +
    '<div class="comp-chart" style="display:flex;align-items:flex-end;justify-content:center;gap:80px;height:50%;position:relative;z-index:10;">' +
      '<div class="comp-bar-group" style="display:flex;flex-direction:column;align-items:center;">' +
        '<div class="comp-value before-value" style="font-family:Space Grotesk,sans-serif;font-size:clamp(32px,6vw,56px);font-weight:700;color:' + beforeColor + ';margin-bottom:20px;opacity:0;">0</div>' +
        '<div class="comp-bar-container" style="width:120px;height:300px;background:rgba(255,255,255,0.1);border-radius:12px;position:relative;overflow:hidden;">' +
          '<div class="comp-bar before-bar" style="position:absolute;bottom:0;left:0;right:0;height:0%;background:linear-gradient(180deg,' + beforeColor + ',' + beforeColor + 'aa);border-radius:12px;"></div>' +
        '</div>' +
        '<div class="comp-label" style="font-family:Inter,sans-serif;font-size:20px;color:rgba(255,255,255,0.7);margin-top:20px;opacity:0;">Before</div>' +
      '</div>' +
      '<div class="comp-arrow-container" style="display:flex;flex-direction:column;align-items:center;justify-content:center;margin-bottom:80px;">' +
        '<div class="comp-reduction" style="font-family:Space Grotesk,sans-serif;font-size:clamp(40px,8vw,72px);font-weight:800;color:' + afterColor + ';opacity:0;">-' + reduction + '%</div>' +
        '<i class="ri-arrow-right-line comp-arrow" style="font-size:48px;color:' + afterColor + ';opacity:0;"></i>' +
      '</div>' +
      '<div class="comp-bar-group" style="display:flex;flex-direction:column;align-items:center;">' +
        '<div class="comp-value after-value" style="font-family:Space Grotesk,sans-serif;font-size:clamp(32px,6vw,56px);font-weight:700;color:' + afterColor + ';margin-bottom:20px;opacity:0;">0</div>' +
        '<div class="comp-bar-container" style="width:120px;height:300px;background:rgba(255,255,255,0.1);border-radius:12px;position:relative;overflow:hidden;">' +
          '<div class="comp-bar after-bar" style="position:absolute;bottom:0;left:0;right:0;height:0%;background:linear-gradient(180deg,' + afterColor + ',' + afterColor + 'aa);border-radius:12px;"></div>' +
        '</div>' +
        '<div class="comp-label" style="font-family:Inter,sans-serif;font-size:20px;color:rgba(255,255,255,0.7);margin-top:20px;opacity:0;">After</div>' +
      '</div>' +
    '</div>' +
    '<div class="comp-unit" style="font-family:Inter,sans-serif;font-size:24px;color:rgba(255,255,255,0.5);margin-top:40px;opacity:0;">' + unit + '</div>' +
  '</div>';

  var bgContainer = container.querySelector('.comp-bg-container');
  var glow1 = VidIn._createGlow(bgContainer, '20%', '50%', 400, beforeColor + '30', 80);
  var glow2 = VidIn._createGlow(bgContainer, '80%', '50%', 400, afterColor + '30', 80);
  var particles = VidIn._createParticles(bgContainer, 15, afterColor);

  var beforeCounter = { value: 0 };
  var afterCounter = { value: 0 };
  var beforeValueEl = container.querySelector('.before-value');
  var afterValueEl = container.querySelector('.after-value');

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: [glow1, glow2], opacity: [0, 1], scale: [0.5, 1], duration: 1500 }, 0);
  tl.add({ targets: '.comp-title', opacity: [0, 1], translateY: [-30, 0], duration: 800 }, 200);
  tl.add({ targets: '.comp-label', opacity: [0, 1], translateY: [20, 0], duration: 600, delay: anime.stagger(200) }, 500);
  tl.add({ targets: '.before-bar', height: ['0%', beforeHeight + '%'], duration: 1200, easing: 'easeOutElastic(1, .6)' }, 800);
  tl.add({ targets: '.before-value', opacity: [0, 1], duration: 300 }, 800);
  tl.add({ targets: beforeCounter, value: [0, beforeValue], round: 1, duration: 1200, easing: 'easeOutExpo', update: function() { beforeValueEl.textContent = Math.round(beforeCounter.value); } }, 800);
  tl.add({ targets: '.comp-arrow', opacity: [0, 1], translateX: [-20, 0], duration: 600 }, 1500);
  tl.add({ targets: '.comp-reduction', opacity: [0, 1], scale: [0.5, 1.1, 1], duration: 800, easing: 'easeOutBack' }, 1600);
  tl.add({ targets: '.after-bar', height: ['0%', afterHeight + '%'], duration: 1200, easing: 'easeOutElastic(1, .6)' }, 1800);
  tl.add({ targets: '.after-value', opacity: [0, 1], duration: 300 }, 1800);
  tl.add({ targets: afterCounter, value: [0, afterValue], round: 1, duration: 1200, easing: 'easeOutExpo', update: function() { afterValueEl.textContent = Math.round(afterCounter.value); } }, 1800);
  tl.add({ targets: '.comp-unit', opacity: [0, 1], duration: 600 }, 2500);
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.3, 0.6)]; }, scale: function() { return [0, anime.random(0.8, 1.2)]; }, duration: 800, delay: anime.stagger(30) }, 600);

  VidIn._animateParticles(particles, 3000);

  return tl;
};

// ============================================================================
// 4. BULLET POINT LIST - 3D icons with staggered floating
// ============================================================================
VidIn.bulletPointList = function(container, opts) {
  var title = opts.title;
  var items = opts.items;
  var icons = opts.icons;
  var primaryColor = opts.primaryColor;
  var secondaryColor = opts.secondaryColor;
  var bgColor = opts.bgColor || '#1a1a2e';

  var iconList = Array.isArray(icons) ? icons : items.map(function() { return icons || 'ri-check-line'; });
  
  var itemsHtml = items.map(function(item, i) {
    var itemColor = i % 2 === 0 ? primaryColor : secondaryColor;
    return '<div class="list-item" style="display:flex;align-items:center;gap:30px;opacity:0;transform:translateX(-60px) scale(0.8);">' +
      '<div class="list-icon-wrap" style="width:80px;height:80px;background:linear-gradient(145deg,' + itemColor + '30,' + itemColor + '10);border-radius:20px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 15px 40px ' + itemColor + '30, 0 8px 20px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.1);border:1px solid ' + itemColor + '25;position:relative;overflow:hidden;">' +
        '<div class="icon-inner-glow" style="position:absolute;inset:0;background:radial-gradient(circle at 30% 30%, ' + itemColor + '50, transparent 60%);opacity:0;"></div>' +
        '<i class="' + iconList[i] + ' list-icon" style="font-size:36px;color:' + itemColor + ';opacity:0;transform:scale(0) rotate(-15deg);filter:drop-shadow(0 3px 10px ' + itemColor + '60);position:relative;z-index:2;"></i>' +
      '</div>' +
      '<span class="list-text" style="font-family:Inter,sans-serif;font-size:clamp(20px,3.5vw,30px);color:#fff;font-weight:500;text-shadow:0 2px 10px rgba(0,0,0,0.3);">' + item + '</span>' +
    '</div>';
  }).join('');

  container.innerHTML = '<div class="vidin-list" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';padding:60px;">' +
    '<div class="list-bg-container" style="position:absolute;inset:0;"></div>' +
    '<h2 class="list-title" style="font-family:Poppins,sans-serif;font-size:clamp(32px,6vw,56px);font-weight:800;color:#fff;margin-bottom:60px;opacity:0;position:relative;z-index:10;text-align:center;text-shadow:0 4px 30px rgba(0,0,0,0.5);">' + title + '</h2>' +
    '<div class="list-container" style="display:flex;flex-direction:column;gap:32px;position:relative;z-index:10;max-width:900px;">' + itemsHtml + '</div>' +
  '</div>';

  var bgContainer = container.querySelector('.list-bg-container');
  var glow1 = VidIn._createGlow(bgContainer, '10%', '30%', 450, primaryColor + '30', 90);
  var glow2 = VidIn._createGlow(bgContainer, '85%', '70%', 400, secondaryColor + '25', 80);
  var particles = VidIn._createParticles(bgContainer, 18, primaryColor);

  var listItems = container.querySelectorAll('.list-item');
  var listIcons = container.querySelectorAll('.list-icon');
  var iconWraps = container.querySelectorAll('.list-icon-wrap');
  var innerGlows = container.querySelectorAll('.icon-inner-glow');

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: [glow1, glow2], opacity: [0, 1], scale: [0.5, 1], duration: 1500 }, 0);
  tl.add({ targets: '.list-title', opacity: [0, 1], translateY: [-40, 0], duration: 1000 }, 200);
  
  // Staggered item entrance - one at a time with 3D effect
  tl.add({ 
    targets: listItems, 
    opacity: [0, 1], 
    translateX: [-60, 0], 
    scale: [0.8, 1],
    duration: 700, 
    delay: anime.stagger(300), // 300ms between each item
    easing: 'easeOutBack' 
  }, 600);
  
  // Icons pop in with rotation and elastic effect
  tl.add({ 
    targets: listIcons, 
    opacity: [0, 1], 
    scale: [0, 1.3, 1], 
    rotate: [-15, 0],
    duration: 600, 
    delay: anime.stagger(300), 
    easing: 'easeOutElastic(1, .5)' 
  }, 900);
  
  // Inner glow fade in
  tl.add({
    targets: innerGlows,
    opacity: [0, 1],
    duration: 500,
    delay: anime.stagger(300)
  }, 1100);
  
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.3, 0.6)]; }, scale: function() { return [0, 1]; }, duration: 800, delay: anime.stagger(30) }, 400);

  VidIn._animateParticles(particles, 3000);
  
  // Continuous floating for each icon wrap (3D hover effect)
  iconWraps.forEach(function(wrap, i) {
    anime({
      targets: wrap,
      translateY: [-6, 6],
      rotateZ: [-2, 2],
      duration: 2000 + i * 150,
      delay: 2500 + i * 200,
      direction: 'alternate',
      loop: true,
      easing: 'easeInOutSine'
    });
    
    // Shadow pulse
    var itemColor = i % 2 === 0 ? primaryColor : secondaryColor;
    anime({
      targets: wrap,
      boxShadow: [
        '0 15px 40px ' + itemColor + '30, 0 8px 20px rgba(0,0,0,0.2)',
        '0 25px 60px ' + itemColor + '45, 0 12px 30px rgba(0,0,0,0.3)',
        '0 15px 40px ' + itemColor + '30, 0 8px 20px rgba(0,0,0,0.2)'
      ],
      duration: 2500 + i * 200,
      delay: 3000 + i * 250,
      direction: 'alternate',
      loop: true,
      easing: 'easeInOutSine'
    });
  });

  return tl;
};

// ============================================================================
// 5. CALL TO ACTION
// ============================================================================
VidIn.callToAction = function(container, opts) {
  var question = opts.question;
  var subtext = opts.subtext;
  var icon = opts.icon;
  var primaryColor = opts.primaryColor;
  var secondaryColor = opts.secondaryColor;
  var bgColor = opts.bgColor || '#1a1a2e';

  container.innerHTML = '<div class="vidin-cta" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';padding:60px;">' +
    '<div class="cta-bg-container" style="position:absolute;inset:0;"></div>' +
    '<div class="cta-icon-container" style="position:relative;margin-bottom:50px;">' +
      '<div class="cta-ring-1" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:200px;height:200px;border:3px solid ' + primaryColor + '30;border-radius:50%;opacity:0;"></div>' +
      '<div class="cta-ring-2" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:260px;height:260px;border:2px solid ' + primaryColor + '20;border-radius:50%;opacity:0;"></div>' +
      '<div class="cta-glow" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:' + primaryColor + ';border-radius:50%;filter:blur(50px);opacity:0;"></div>' +
      '<i class="' + icon + ' cta-icon" style="font-size:100px;color:' + primaryColor + ';position:relative;z-index:2;opacity:0;"></i>' +
    '</div>' +
    '<h2 class="cta-question" style="font-family:Poppins,sans-serif;font-size:clamp(28px,5vw,52px);font-weight:700;color:#fff;text-align:center;margin:0;opacity:0;position:relative;z-index:10;max-width:90%;line-height:1.3;">' + question + '</h2>' +
    '<p class="cta-subtext" style="font-family:Inter,sans-serif;font-size:clamp(16px,3vw,24px);color:' + secondaryColor + ';margin-top:30px;text-align:center;opacity:0;position:relative;z-index:10;">' + subtext + '</p>' +
  '</div>';

  var bgContainer = container.querySelector('.cta-bg-container');
  var glow1 = VidIn._createGlow(bgContainer, '20%', '30%', 400, primaryColor + '20', 80);
  var glow2 = VidIn._createGlow(bgContainer, '80%', '70%', 350, secondaryColor + '20', 70);
  var particles = VidIn._createParticles(bgContainer, 20, primaryColor);

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: [glow1, glow2], opacity: [0, 1], scale: [0.5, 1], duration: 1500 }, 0);
  tl.add({ targets: '.cta-ring-1', opacity: [0, 1], scale: [0.5, 1], duration: 1000 }, 200);
  tl.add({ targets: '.cta-ring-2', opacity: [0, 1], scale: [0.3, 1], duration: 1200 }, 300);
  tl.add({ targets: '.cta-glow', opacity: [0, 0.6], scale: [0.5, 1.2], duration: 1000 }, 400);
  tl.add({ targets: '.cta-icon', opacity: [0, 1], scale: [0, 1.2, 1], translateY: [-50, 0], duration: 1000, easing: 'easeOutElastic(1, .5)' }, 500);
  tl.add({ targets: '.cta-question', opacity: [0, 1], translateY: [40, 0], duration: 1000 }, 900);
  tl.add({ targets: '.cta-subtext', opacity: [0, 1], translateY: [20, 0], duration: 800 }, 1300);
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.3, 0.6)]; }, scale: function() { return [0, 1]; }, duration: 800, delay: anime.stagger(30) }, 300);

  anime({ targets: '.cta-icon', translateY: [-5, 5], duration: 1500, delay: 2000, direction: 'alternate', loop: true, easing: 'easeInOutSine' });
  anime({ targets: ['.cta-ring-1', '.cta-ring-2'], scale: [1, 1.1], opacity: [1, 0.5], duration: 2000, delay: 2500, direction: 'alternate', loop: true, easing: 'easeInOutSine' });
  VidIn._animateParticles(particles, 2500);

  return tl;
};

// ============================================================================
// 6. KEY TAKEAWAY
// ============================================================================
VidIn.keyTakeaway = function(container, opts) {
  var takeaway = opts.takeaway;
  var icon = opts.icon;
  var primaryColor = opts.primaryColor;
  var secondaryColor = opts.secondaryColor;
  var bgColor = opts.bgColor || '#1a1a2e';

  container.innerHTML = '<div class="vidin-takeaway" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';padding:60px;">' +
    '<div class="takeaway-bg-container" style="position:absolute;inset:0;"></div>' +
    '<div class="takeaway-badge" style="display:flex;align-items:center;gap:15px;background:' + primaryColor + '20;padding:15px 30px;border-radius:50px;margin-bottom:40px;opacity:0;">' +
      '<i class="ri-lightbulb-flash-fill" style="font-size:24px;color:' + primaryColor + ';"></i>' +
      '<span style="font-family:Inter,sans-serif;font-size:16px;color:' + primaryColor + ';font-weight:600;text-transform:uppercase;letter-spacing:2px;">Key Takeaway</span>' +
    '</div>' +
    '<div class="takeaway-icon-wrap" style="margin-bottom:40px;position:relative;">' +
      '<div class="takeaway-glow" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:180px;height:180px;background:' + primaryColor + ';border-radius:50%;filter:blur(60px);opacity:0;"></div>' +
      '<i class="' + icon + ' takeaway-icon" style="font-size:90px;color:' + primaryColor + ';position:relative;z-index:2;opacity:0;"></i>' +
    '</div>' +
    '<h2 class="takeaway-text" style="font-family:Poppins,sans-serif;font-size:clamp(32px,6vw,60px);font-weight:700;color:#fff;text-align:center;margin:0;opacity:0;position:relative;z-index:10;max-width:90%;line-height:1.3;">' + takeaway + '</h2>' +
  '</div>';

  var bgContainer = container.querySelector('.takeaway-bg-container');
  var glow1 = VidIn._createGlow(bgContainer, '30%', '30%', 350, primaryColor + '25', 70);
  var glow2 = VidIn._createGlow(bgContainer, '70%', '70%', 300, secondaryColor + '20', 60);
  var particles = VidIn._createParticles(bgContainer, 15, primaryColor);

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: [glow1, glow2], opacity: [0, 1], scale: [0.5, 1], duration: 1500 }, 0);
  tl.add({ targets: '.takeaway-badge', opacity: [0, 1], translateY: [-20, 0], scale: [0.9, 1], duration: 800 }, 200);
  tl.add({ targets: '.takeaway-glow', opacity: [0, 0.5], scale: [0.3, 1.2], duration: 1000 }, 400);
  tl.add({ targets: '.takeaway-icon', opacity: [0, 1], scale: [0, 1.2, 1], duration: 800, easing: 'easeOutElastic(1, .5)' }, 600);
  tl.add({ targets: '.takeaway-text', opacity: [0, 1], translateY: [40, 0], duration: 1000 }, 900);
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.3, 0.6)]; }, scale: function() { return [0, 1]; }, duration: 800, delay: anime.stagger(30) }, 300);

  anime({ targets: '.takeaway-icon', translateY: [-5, 5], duration: 2000, delay: 2000, direction: 'alternate', loop: true, easing: 'easeInOutSine' });
  VidIn._animateParticles(particles, 2500);

  return tl;
};

// ============================================================================
// 7. ICON GRID REVEAL - 3D-like icons with continuous floating
// ============================================================================
VidIn.iconGridReveal = function(container, opts) {
  var items = opts.items;
  var columns = opts.columns || 2;
  var title = opts.title;
  var primaryColor = opts.primaryColor;
  var secondaryColor = opts.secondaryColor;
  var bgColor = opts.bgColor || '#1a1a2e';

  // Create 3D-like icon cards with gradient, shadow, and perspective
  var gridItems = items.map(function(item, i) {
    var itemColor = i % 2 === 0 ? primaryColor : secondaryColor;
    return '<div class="grid-item" style="display:flex;flex-direction:column;align-items:center;gap:24px;opacity:0;transform:scale(0.3) translateY(60px) rotateX(20deg);perspective:1000px;">' +
      '<div class="grid-icon-card" style="width:140px;height:140px;background:linear-gradient(145deg,' + itemColor + '25,' + itemColor + '08);border-radius:32px;display:flex;align-items:center;justify-content:center;box-shadow:0 20px 60px ' + itemColor + '30, 0 10px 30px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);border:1px solid ' + itemColor + '30;transform-style:preserve-3d;position:relative;overflow:hidden;">' +
        '<div class="icon-glow" style="position:absolute;inset:0;background:radial-gradient(circle at 30% 30%, ' + itemColor + '40, transparent 60%);opacity:0;"></div>' +
        '<div class="icon-shine" style="position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.1) 50%, transparent 60%);transform:rotate(0deg);"></div>' +
        '<i class="' + item.icon + ' grid-icon" style="font-size:64px;color:' + itemColor + ';filter:drop-shadow(0 4px 15px ' + itemColor + '80);position:relative;z-index:2;"></i>' +
      '</div>' +
      '<span class="grid-label" style="font-family:Poppins,sans-serif;font-size:20px;color:#fff;text-align:center;font-weight:600;text-shadow:0 2px 10px rgba(0,0,0,0.5);">' + item.label + '</span>' +
    '</div>';
  }).join('');

  container.innerHTML = '<div class="vidin-grid" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';padding:60px;">' +
    '<div class="grid-bg-container" style="position:absolute;inset:0;"></div>' +
    '<h2 class="grid-title" style="font-family:Poppins,sans-serif;font-size:clamp(32px,6vw,56px);font-weight:800;color:#fff;margin-bottom:70px;opacity:0;position:relative;z-index:10;text-shadow:0 4px 30px rgba(0,0,0,0.5);">' + title + '</h2>' +
    '<div class="grid-container" style="display:grid;grid-template-columns:repeat(' + columns + ',1fr);gap:60px;position:relative;z-index:10;">' + gridItems + '</div>' +
  '</div>';

  var bgContainer = container.querySelector('.grid-bg-container');
  var glow1 = VidIn._createGlow(bgContainer, '50%', '50%', 700, primaryColor + '25', 120);
  glow1.style.transform = 'translate(-50%, -50%) scale(0.5)';
  var glow2 = VidIn._createGlow(bgContainer, '20%', '30%', 400, secondaryColor + '20', 80);
  var glow3 = VidIn._createGlow(bgContainer, '80%', '70%', 400, primaryColor + '20', 80);
  var particles = VidIn._createParticles(bgContainer, 25, primaryColor);

  var gridItemEls = container.querySelectorAll('.grid-item');
  var iconCards = container.querySelectorAll('.grid-icon-card');
  var iconGlows = container.querySelectorAll('.icon-glow');

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  // Background glows
  tl.add({ targets: [glow1, glow2, glow3], opacity: [0, 1], scale: [0.5, 1.2], duration: 2000, delay: anime.stagger(200) }, 0);
  
  // Title entrance
  tl.add({ targets: '.grid-title', opacity: [0, 1], translateY: [-50, 0], duration: 1000 }, 200);
  
  // Icons entrance with 3D effect - staggered one by one
  tl.add({ 
    targets: gridItemEls, 
    opacity: [0, 1], 
    scale: [0.3, 1], 
    translateY: [60, 0],
    rotateX: [20, 0],
    duration: 800, 
    delay: anime.stagger(250), // Stagger each icon 250ms apart
    easing: 'easeOutBack'
  }, 600);
  
  // Icon inner glow
  tl.add({
    targets: iconGlows,
    opacity: [0, 1],
    duration: 600,
    delay: anime.stagger(250),
    easing: 'easeOutExpo'
  }, 900);
  
  // Particles
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.2, 0.6)]; }, scale: function() { return [0, 1]; }, duration: 1000, delay: anime.stagger(40) }, 400);

  VidIn._animateParticles(particles, 2500);
  
  // Continuous floating animation for each icon card (3D hover effect)
  iconCards.forEach(function(card, i) {
    anime({
      targets: card,
      translateY: [-8, 8],
      rotateY: [-3, 3],
      rotateX: [-2, 2],
      duration: 2500 + i * 200, // Slightly different duration for each
      delay: 2000 + i * 100,
      direction: 'alternate',
      loop: true,
      easing: 'easeInOutSine'
    });
    
    // Box shadow pulse for 3D depth
    anime({
      targets: card,
      boxShadow: [
        '0 20px 60px ' + (i % 2 === 0 ? primaryColor : secondaryColor) + '30, 0 10px 30px rgba(0,0,0,0.3)',
        '0 30px 80px ' + (i % 2 === 0 ? primaryColor : secondaryColor) + '50, 0 15px 40px rgba(0,0,0,0.4)',
        '0 20px 60px ' + (i % 2 === 0 ? primaryColor : secondaryColor) + '30, 0 10px 30px rgba(0,0,0,0.3)'
      ],
      duration: 3000 + i * 200,
      delay: 2500 + i * 150,
      direction: 'alternate',
      loop: true,
      easing: 'easeInOutSine'
    });
  });

  return tl;
};

// ============================================================================
// 8. MULTI-STAT REVEAL
// ============================================================================
VidIn.multiStatReveal = function(container, opts) {
  var stats = opts.stats;
  var title = opts.title;
  var primaryColor = opts.primaryColor;
  var secondaryColor = opts.secondaryColor;
  var bgColor = opts.bgColor || '#1a1a2e';

  var statsHtml = stats.map(function(stat, i) {
    var statColor = i % 2 === 0 ? primaryColor : secondaryColor;
    return '<div class="multi-stat-item" style="display:flex;flex-direction:column;align-items:center;opacity:0;transform:translateY(40px);">' +
      '<div class="multi-stat-icon-wrap" style="margin-bottom:15px;">' +
        '<i class="' + stat.icon + ' multi-stat-icon" style="font-size:40px;color:' + statColor + ';opacity:0;"></i>' +
      '</div>' +
      '<div class="multi-stat-value-wrap" style="display:flex;align-items:baseline;">' +
        '<span class="multi-stat-value" data-value="' + stat.value + '" style="font-family:Space Grotesk,sans-serif;font-size:clamp(48px,10vw,80px);font-weight:700;color:#fff;">0</span>' +
        '<span class="multi-stat-suffix" style="font-family:Space Grotesk,sans-serif;font-size:clamp(24px,5vw,40px);color:' + statColor + ';margin-left:5px;opacity:0;">' + (stat.suffix || '') + '</span>' +
      '</div>' +
      '<span class="multi-stat-label" style="font-family:Inter,sans-serif;font-size:18px;color:rgba(255,255,255,0.6);margin-top:10px;text-transform:uppercase;letter-spacing:1px;opacity:0;">' + stat.label + '</span>' +
    '</div>';
  }).join('');

  container.innerHTML = '<div class="vidin-multi-stat" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';padding:60px;">' +
    '<div class="multi-bg-container" style="position:absolute;inset:0;"></div>' +
    '<h2 class="multi-title" style="font-family:Poppins,sans-serif;font-size:clamp(28px,5vw,48px);font-weight:700;color:#fff;margin-bottom:60px;opacity:0;position:relative;z-index:10;">' + title + '</h2>' +
    '<div class="multi-stats-container" style="display:flex;gap:80px;position:relative;z-index:10;flex-wrap:wrap;justify-content:center;">' + statsHtml + '</div>' +
  '</div>';

  var bgContainer = container.querySelector('.multi-bg-container');
  var glow1 = VidIn._createGlow(bgContainer, '30%', '50%', 400, primaryColor + '25', 80);
  var glow2 = VidIn._createGlow(bgContainer, '70%', '50%', 400, secondaryColor + '25', 80);
  var particles = VidIn._createParticles(bgContainer, 18, primaryColor);

  var statItems = container.querySelectorAll('.multi-stat-item');
  var statValues = container.querySelectorAll('.multi-stat-value');

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: [glow1, glow2], opacity: [0, 1], scale: [0.5, 1], duration: 1500 }, 0);
  tl.add({ targets: '.multi-title', opacity: [0, 1], translateY: [-30, 0], duration: 800 }, 200);
  tl.add({ targets: statItems, opacity: [0, 1], translateY: [40, 0], duration: 800, delay: anime.stagger(250), easing: 'easeOutBack' }, 600);
  tl.add({ targets: '.multi-stat-icon', opacity: [0, 1], scale: [0, 1.2, 1], duration: 500, delay: anime.stagger(250), easing: 'easeOutElastic(1, .6)' }, 800);

  statValues.forEach(function(el, i) {
    var targetValue = parseInt(el.dataset.value);
    var counter = { value: 0 };
    
    tl.add({
      targets: counter,
      value: [0, targetValue],
      round: 1,
      duration: 1200,
      easing: 'easeOutExpo',
      update: function() { el.textContent = Math.round(counter.value); }
    }, 900 + i * 250);
  });

  tl.add({ targets: '.multi-stat-suffix', opacity: [0, 1], translateX: [-10, 0], duration: 400, delay: anime.stagger(250) }, 1400);
  tl.add({ targets: '.multi-stat-label', opacity: [0, 1], duration: 400, delay: anime.stagger(250) }, 1600);
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.3, 0.6)]; }, scale: function() { return [0, 1]; }, duration: 800, delay: anime.stagger(30) }, 400);

  VidIn._animateParticles(particles, 3000);

  return tl;
};

// ============================================================================
// 9. IMPACT METRICS
// ============================================================================
VidIn.impactMetrics = function(container, opts) {
  var metrics = opts.metrics;
  var title = opts.title;
  var primaryColor = opts.primaryColor;
  var secondaryColor = opts.secondaryColor;
  var bgColor = opts.bgColor || '#1a1a2e';

  var colors = [primaryColor, secondaryColor, primaryColor];
  
  var metricsHtml = metrics.slice(0, 3).map(function(m, i) {
    return '<div class="impact-item" style="display:flex;flex-direction:column;align-items:center;opacity:0;transform:translateY(50px);">' +
      '<div class="impact-icon-wrap" style="width:80px;height:80px;background:linear-gradient(135deg,' + colors[i] + '30,' + colors[i] + '10);border-radius:50%;display:flex;align-items:center;justify-content:center;margin-bottom:20px;box-shadow:0 10px 30px ' + colors[i] + '20;">' +
        '<i class="' + m.icon + ' impact-icon" style="font-size:36px;color:' + colors[i] + ';opacity:0;"></i>' +
      '</div>' +
      '<span class="impact-value" data-value="' + m.value + '" style="font-family:Space Grotesk,sans-serif;font-size:clamp(36px,8vw,60px);font-weight:700;color:#fff;">0</span>' +
      '<span class="impact-suffix" style="font-family:Space Grotesk,sans-serif;font-size:24px;color:' + colors[i] + ';opacity:0;">' + (m.suffix || '') + '</span>' +
      '<span class="impact-label" style="font-family:Inter,sans-serif;font-size:16px;color:rgba(255,255,255,0.6);margin-top:10px;text-align:center;opacity:0;">' + m.label + '</span>' +
    '</div>';
  }).join('');

  container.innerHTML = '<div class="vidin-impact" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';padding:60px;">' +
    '<div class="impact-bg-container" style="position:absolute;inset:0;"></div>' +
    '<h2 class="impact-title" style="font-family:Poppins,sans-serif;font-size:clamp(28px,5vw,48px);font-weight:700;color:#fff;margin-bottom:60px;opacity:0;position:relative;z-index:10;">' + title + '</h2>' +
    '<div class="impact-container" style="display:flex;gap:60px;position:relative;z-index:10;flex-wrap:wrap;justify-content:center;">' + metricsHtml + '</div>' +
  '</div>';

  var bgContainer = container.querySelector('.impact-bg-container');
  var glow1 = VidIn._createGlow(bgContainer, '15%', '50%', 350, primaryColor + '25', 70);
  var glow2 = VidIn._createGlow(bgContainer, '50%', '50%', 400, secondaryColor + '20', 80);
  var glow3 = VidIn._createGlow(bgContainer, '85%', '50%', 350, primaryColor + '25', 70);
  var particles = VidIn._createParticles(bgContainer, 15, primaryColor);

  var impactItems = container.querySelectorAll('.impact-item');
  var impactValues = container.querySelectorAll('.impact-value');

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: [glow1, glow2, glow3], opacity: [0, 1], scale: [0.5, 1], duration: 1500, delay: anime.stagger(200) }, 0);
  tl.add({ targets: '.impact-title', opacity: [0, 1], translateY: [-30, 0], duration: 800 }, 200);
  tl.add({ targets: impactItems, opacity: [0, 1], translateY: [50, 0], duration: 800, delay: anime.stagger(200), easing: 'easeOutBack' }, 600);
  tl.add({ targets: '.impact-icon', opacity: [0, 1], scale: [0, 1.2, 1], duration: 600, delay: anime.stagger(200), easing: 'easeOutElastic(1, .6)' }, 800);

  impactValues.forEach(function(el, i) {
    var targetValue = parseInt(el.dataset.value);
    var counter = { value: 0 };
    
    tl.add({
      targets: counter,
      value: [0, targetValue],
      round: 1,
      duration: 1200,
      easing: 'easeOutExpo',
      update: function() { el.textContent = Math.round(counter.value); }
    }, 1000 + i * 200);
  });

  tl.add({ targets: '.impact-suffix', opacity: [0, 1], duration: 400, delay: anime.stagger(200) }, 1500);
  tl.add({ targets: '.impact-label', opacity: [0, 1], duration: 400, delay: anime.stagger(200) }, 1700);
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.3, 0.5)]; }, scale: function() { return [0, 1]; }, duration: 800, delay: anime.stagger(30) }, 400);

  VidIn._animateParticles(particles, 3000);

  return tl;
};

// ============================================================================
// 10. CELEBRATION FINALE
// ============================================================================
VidIn.celebrationFinale = function(container, opts) {
  var title = opts.title;
  var subtitle = opts.subtitle;
  var primaryColor = opts.primaryColor;
  var secondaryColor = opts.secondaryColor;
  var bgColor = opts.bgColor || '#1a1a2e';

  container.innerHTML = '<div class="vidin-celebration" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';padding:60px;">' +
    '<div class="celebration-bg-container" style="position:absolute;inset:0;"></div>' +
    '<div class="celebration-confetti" style="position:absolute;inset:0;pointer-events:none;"></div>' +
    '<div class="celebration-icon-wrap" style="margin-bottom:40px;position:relative;">' +
      '<div class="celebration-ring-1" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:200px;height:200px;border:4px solid ' + primaryColor + '40;border-radius:50%;opacity:0;"></div>' +
      '<div class="celebration-ring-2" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:280px;height:280px;border:3px solid ' + secondaryColor + '30;border-radius:50%;opacity:0;"></div>' +
      '<div class="celebration-glow" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:150px;height:150px;background:' + primaryColor + ';border-radius:50%;filter:blur(50px);opacity:0;"></div>' +
      '<i class="ri-trophy-fill celebration-icon" style="font-size:120px;color:' + primaryColor + ';position:relative;z-index:2;opacity:0;"></i>' +
    '</div>' +
    '<h1 class="celebration-title" style="font-family:Poppins,sans-serif;font-size:clamp(40px,8vw,80px);font-weight:800;color:#fff;text-align:center;margin:0;opacity:0;position:relative;z-index:10;text-shadow:0 4px 60px rgba(0,0,0,0.5);">' + title + '</h1>' +
    '<p class="celebration-subtitle" style="font-family:Inter,sans-serif;font-size:clamp(18px,3vw,28px);color:' + secondaryColor + ';margin-top:25px;text-align:center;opacity:0;position:relative;z-index:10;">' + subtitle + '</p>' +
  '</div>';

  var bgContainer = container.querySelector('.celebration-bg-container');
  var confettiContainer = container.querySelector('.celebration-confetti');
  
  var glow1 = VidIn._createGlow(bgContainer, '50%', '40%', 500, primaryColor + '30', 100);
  glow1.style.transform = 'translate(-50%, -50%) scale(0.5)';
  var particles = VidIn._createParticles(bgContainer, 20, primaryColor);

  // Create confetti
  var confettiColors = [primaryColor, secondaryColor, '#FFD700', '#FF6B6B', '#4ECDC4'];
  for (var i = 0; i < 50; i++) {
    var confetti = document.createElement('div');
    var size = 8 + Math.random() * 8;
    confetti.style.cssText = 'position:absolute;left:' + (Math.random() * 100) + '%;top:-20px;width:' + size + 'px;height:' + size + 'px;background:' + confettiColors[Math.floor(Math.random() * confettiColors.length)] + ';border-radius:' + (Math.random() > 0.5 ? '50%' : '2px') + ';opacity:0;';
    confetti.className = 'confetti-piece';
    confettiContainer.appendChild(confetti);
  }

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: glow1, opacity: [0, 1], scale: [0.5, 1.5], duration: 2000 }, 0);
  tl.add({ targets: '.celebration-ring-1', opacity: [0, 1], scale: [0.3, 1], duration: 1000, easing: 'easeOutBack' }, 200);
  tl.add({ targets: '.celebration-ring-2', opacity: [0, 1], scale: [0.2, 1], duration: 1200 }, 300);
  tl.add({ targets: '.celebration-glow', opacity: [0, 0.7], scale: [0.3, 1.3], duration: 1000 }, 400);
  tl.add({ targets: '.celebration-icon', opacity: [0, 1], scale: [0, 1.3, 1], translateY: [-50, 0], duration: 1200, easing: 'easeOutElastic(1, .4)' }, 500);
  tl.add({ targets: '.celebration-title', opacity: [0, 1], scale: [0.8, 1], translateY: [40, 0], duration: 1000 }, 900);
  tl.add({ targets: '.celebration-subtitle', opacity: [0, 1], translateY: [20, 0], duration: 800 }, 1200);
  tl.add({ targets: '.confetti-piece', translateY: function() { return [0, anime.random(400, 800)]; }, translateX: function() { return anime.random(-100, 100); }, rotate: function() { return anime.random(0, 720); }, opacity: [0, 1, 1, 0], duration: function() { return anime.random(2000, 3000); }, delay: anime.stagger(30, { from: 'random' }), easing: 'easeOutQuad' }, 800);
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.3, 0.6)]; }, scale: function() { return [0, 1]; }, duration: 800, delay: anime.stagger(30) }, 300);

  anime({ targets: ['.celebration-ring-1', '.celebration-ring-2'], scale: [1, 1.15], opacity: [1, 0.5], duration: 1500, delay: 2500, direction: 'alternate', loop: true, easing: 'easeInOutSine' });
  VidIn._animateParticles(particles, 2500);

  return tl;
};

// ============================================================================
// 11. PROCESS FLOW
// ============================================================================
VidIn.processFlow = function(container, opts) {
  var steps = opts.steps;
  var primaryColor = opts.primaryColor;
  var secondaryColor = opts.secondaryColor;
  var bgColor = opts.bgColor || '#1a1a2e';

  var stepsHtml = steps.map(function(step, i) {
    var html = '<div class="flow-step" style="display:flex;flex-direction:column;align-items:center;opacity:0;">' +
      '<div class="flow-step-num" style="width:60px;height:60px;background:linear-gradient(135deg,' + primaryColor + ',' + secondaryColor + ');border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:Space Grotesk,sans-serif;font-size:24px;font-weight:700;color:#fff;box-shadow:0 10px 30px ' + primaryColor + '40;">' + (i + 1) + '</div>' +
      '<span class="flow-step-label" style="font-family:Inter,sans-serif;font-size:18px;color:#fff;margin-top:20px;text-align:center;max-width:150px;opacity:0;">' + step + '</span>' +
    '</div>';
    if (i < steps.length - 1) {
      html += '<div class="flow-connector" style="width:80px;height:3px;background:linear-gradient(90deg,' + primaryColor + ',' + secondaryColor + ');margin:0 10px;margin-bottom:50px;transform:scaleX(0);transform-origin:left;"></div>';
    }
    return html;
  }).join('');

  container.innerHTML = '<div class="vidin-flow" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';padding:60px;">' +
    '<div class="flow-bg-container" style="position:absolute;inset:0;"></div>' +
    '<h2 class="flow-title" style="font-family:Poppins,sans-serif;font-size:clamp(28px,5vw,48px);font-weight:700;color:#fff;margin-bottom:60px;opacity:0;position:relative;z-index:10;">The Process</h2>' +
    '<div class="flow-container" style="display:flex;align-items:center;position:relative;z-index:10;flex-wrap:wrap;justify-content:center;">' + stepsHtml + '</div>' +
  '</div>';

  var bgContainer = container.querySelector('.flow-bg-container');
  var glow1 = VidIn._createGlow(bgContainer, '50%', '50%', 600, primaryColor + '15', 100);
  glow1.style.transform = 'translate(-50%, -50%) scale(0.5)';
  var particles = VidIn._createParticles(bgContainer, 15, primaryColor);

  var flowSteps = container.querySelectorAll('.flow-step');
  var connectors = container.querySelectorAll('.flow-connector');
  var labels = container.querySelectorAll('.flow-step-label');

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: glow1, opacity: [0, 1], scale: [0.5, 1.2], duration: 2000 }, 0);
  tl.add({ targets: '.flow-title', opacity: [0, 1], translateY: [-30, 0], duration: 800 }, 200);

  flowSteps.forEach(function(step, i) {
    tl.add({ targets: step, opacity: [0, 1], scale: [0.5, 1], duration: 600, easing: 'easeOutBack' }, 600 + i * 400);
    if (connectors[i]) {
      tl.add({ targets: connectors[i], scaleX: [0, 1], duration: 400 }, 900 + i * 400);
    }
  });

  tl.add({ targets: labels, opacity: [0, 1], translateY: [10, 0], duration: 400, delay: anime.stagger(200) }, 800);
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.2, 0.5)]; }, scale: function() { return [0, 1]; }, duration: 800, delay: anime.stagger(30) }, 400);

  VidIn._animateParticles(particles, 3500);

  return tl;
};

// ============================================================================
// 12. QUOTE REVEAL
// ============================================================================
VidIn.quoteReveal = function(container, opts) {
  var quote = opts.quote;
  var author = opts.author;
  var primaryColor = opts.primaryColor;
  var secondaryColor = opts.secondaryColor;
  var bgColor = opts.bgColor || '#1a1a2e';

  container.innerHTML = '<div class="vidin-quote" style="width:100%;height:100%;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;background:' + bgColor + ';padding:80px;">' +
    '<div class="quote-bg-container" style="position:absolute;inset:0;"></div>' +
    '<div class="quote-mark-left" style="position:absolute;left:10%;top:25%;font-family:Georgia,serif;font-size:200px;color:' + primaryColor + '20;opacity:0;">"</div>' +
    '<div class="quote-mark-right" style="position:absolute;right:10%;bottom:25%;font-family:Georgia,serif;font-size:200px;color:' + primaryColor + '20;opacity:0;">"</div>' +
    '<blockquote class="quote-text" style="font-family:Poppins,sans-serif;font-size:clamp(24px,4vw,42px);font-weight:500;color:#fff;text-align:center;line-height:1.6;max-width:85%;margin:0;opacity:0;position:relative;z-index:10;">' + quote + '</blockquote>' +
    '<div class="quote-line" style="width:0;height:3px;background:linear-gradient(90deg,transparent,' + primaryColor + ',transparent);margin:40px 0;"></div>' +
    '<cite class="quote-author" style="font-family:Inter,sans-serif;font-size:20px;color:' + secondaryColor + ';font-style:normal;opacity:0;position:relative;z-index:10;">— ' + author + '</cite>' +
  '</div>';

  var bgContainer = container.querySelector('.quote-bg-container');
  var glow1 = VidIn._createGlow(bgContainer, '50%', '50%', 500, primaryColor + '15', 100);
  glow1.style.transform = 'translate(-50%, -50%) scale(0.5)';
  var particles = VidIn._createParticles(bgContainer, 12, primaryColor);

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  tl.add({ targets: glow1, opacity: [0, 1], scale: [0.5, 1.3], duration: 2000 }, 0);
  tl.add({ targets: '.quote-mark-left', opacity: [0, 1], translateX: [-30, 0], duration: 1000 }, 200);
  tl.add({ targets: '.quote-mark-right', opacity: [0, 1], translateX: [30, 0], duration: 1000 }, 400);
  tl.add({ targets: '.quote-text', opacity: [0, 1], translateY: [30, 0], duration: 1200 }, 500);
  tl.add({ targets: '.quote-line', width: ['0%', '30%'], duration: 800 }, 1200);
  tl.add({ targets: '.quote-author', opacity: [0, 1], translateY: [15, 0], duration: 600 }, 1500);
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.2, 0.5)]; }, scale: function() { return [0, 1]; }, duration: 800, delay: anime.stagger(30) }, 300);

  VidIn._animateParticles(particles, 2500);

  return tl;
};

// ============================================================================
// 13. CONCEPT SHOWCASE - Best for visualizing key terms from voiceover
// ============================================================================
VidIn.conceptShowcase = function(container, opts) {
  var concepts = opts.concepts; // Array of { icon, label, description }
  var title = opts.title;
  var primaryColor = opts.primaryColor;
  var secondaryColor = opts.secondaryColor;
  var bgColor = opts.bgColor || '#1a1a2e';

  // Calculate layout based on number of concepts
  var layout = concepts.length <= 3 ? 'row' : 'grid';
  var columns = concepts.length <= 4 ? concepts.length : Math.ceil(concepts.length / 2);
  
  var conceptsHtml = concepts.map(function(concept, i) {
    var conceptColor = [primaryColor, secondaryColor, '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'][i % 6];
    var delay = i * 0.15;
    
    return '<div class="concept-card" data-delay="' + delay + '" style="' +
      'display:flex;flex-direction:column;align-items:center;gap:20px;padding:30px;' +
      'background:linear-gradient(160deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));' +
      'border-radius:28px;border:1px solid rgba(255,255,255,0.1);' +
      'box-shadow:0 25px 60px rgba(0,0,0,0.4), 0 10px 25px ' + conceptColor + '20;' +
      'opacity:0;transform:translateY(80px) scale(0.7) rotateX(25deg);' +
      'perspective:1000px;min-width:200px;max-width:280px;">' +
      
      // 3D Icon container
      '<div class="concept-icon-container" style="' +
        'width:120px;height:120px;position:relative;perspective:500px;transform-style:preserve-3d;">' +
        
        // Background glow
        '<div class="concept-icon-glow" style="' +
          'position:absolute;inset:-20px;' +
          'background:radial-gradient(circle, ' + conceptColor + '50, transparent 70%);' +
          'filter:blur(30px);opacity:0;transform:scale(0.5);">' +
        '</div>' +
        
        // Icon card with 3D effect
        '<div class="concept-icon-card" style="' +
          'position:absolute;inset:0;' +
          'background:linear-gradient(135deg, ' + conceptColor + '40, ' + conceptColor + '15);' +
          'border-radius:28px;' +
          'border:2px solid ' + conceptColor + '50;' +
          'box-shadow:' +
            '0 20px 50px ' + conceptColor + '40, ' +
            'inset 0 2px 0 rgba(255,255,255,0.2), ' +
            'inset 0 -2px 0 rgba(0,0,0,0.1);' +
          'display:flex;align-items:center;justify-content:center;' +
          'overflow:hidden;transform-style:preserve-3d;">' +
          
          // Shine effect
          '<div class="concept-shine" style="' +
            'position:absolute;inset:0;' +
            'background:linear-gradient(115deg, transparent 30%, rgba(255,255,255,0.25) 45%, rgba(255,255,255,0.1) 50%, transparent 65%);' +
            'transform:translateX(-100%);">' +
          '</div>' +
          
          // Icon
          '<i class="' + concept.icon + ' concept-icon" style="' +
            'font-size:56px;color:#fff;position:relative;z-index:2;' +
            'filter:drop-shadow(0 4px 15px ' + conceptColor + ') drop-shadow(0 2px 5px rgba(0,0,0,0.3));' +
            'transform:scale(0) rotate(-20deg);">' +
          '</i>' +
        '</div>' +
      '</div>' +
      
      // Label
      '<div class="concept-label" style="' +
        'font-family:Poppins,sans-serif;font-size:22px;font-weight:700;' +
        'color:#fff;text-align:center;text-shadow:0 2px 10px rgba(0,0,0,0.3);opacity:0;transform:translateY(10px);">' +
        concept.label +
      '</div>' +
      
      // Optional description
      (concept.description ? 
        '<div class="concept-desc" style="' +
          'font-family:Inter,sans-serif;font-size:14px;color:rgba(255,255,255,0.6);' +
          'text-align:center;line-height:1.5;opacity:0;transform:translateY(10px);">' +
          concept.description +
        '</div>' : '') +
    '</div>';
  }).join('');

  container.innerHTML = '<div class="vidin-concepts" style="' +
    'width:100%;height:100%;position:relative;' +
    'display:flex;flex-direction:column;justify-content:center;align-items:center;' +
    'overflow:hidden;background:' + bgColor + ';padding:60px;">' +
    '<div class="concepts-bg-container" style="position:absolute;inset:0;"></div>' +
    
    // Title
    '<h2 class="concepts-title" style="' +
      'font-family:Poppins,sans-serif;font-size:clamp(28px,5vw,52px);font-weight:800;' +
      'color:#fff;margin-bottom:60px;opacity:0;transform:translateY(-30px);' +
      'position:relative;z-index:10;text-align:center;text-shadow:0 4px 30px rgba(0,0,0,0.5);">' +
      title +
    '</h2>' +
    
    // Concepts grid/row
    '<div class="concepts-container" style="' +
      'display:flex;flex-wrap:wrap;justify-content:center;gap:40px;' +
      'position:relative;z-index:10;max-width:1200px;">' +
      conceptsHtml +
    '</div>' +
  '</div>';

  var bgContainer = container.querySelector('.concepts-bg-container');
  
  // Create multiple glows
  var glow1 = VidIn._createGlow(bgContainer, '30%', '40%', 500, primaryColor + '20', 100);
  var glow2 = VidIn._createGlow(bgContainer, '70%', '60%', 450, secondaryColor + '20', 90);
  var glow3 = VidIn._createGlow(bgContainer, '50%', '80%', 400, '#10B98120', 80);
  var particles = VidIn._createParticles(bgContainer, 30, primaryColor);

  var conceptCards = container.querySelectorAll('.concept-card');
  var iconGlows = container.querySelectorAll('.concept-icon-glow');
  var iconCards = container.querySelectorAll('.concept-icon-card');
  var icons = container.querySelectorAll('.concept-icon');
  var shines = container.querySelectorAll('.concept-shine');
  var labels = container.querySelectorAll('.concept-label');
  var descs = container.querySelectorAll('.concept-desc');

  var tl = anime.timeline({ easing: 'easeOutExpo' });

  // Background glows
  tl.add({ targets: [glow1, glow2, glow3], opacity: [0, 1], scale: [0.5, 1.3], duration: 2000, delay: anime.stagger(150) }, 0);
  
  // Title
  tl.add({ targets: '.concepts-title', opacity: [0, 1], translateY: [-30, 0], duration: 1000 }, 200);
  
  // Cards entrance - staggered with 3D rotation
  tl.add({
    targets: conceptCards,
    opacity: [0, 1],
    translateY: [80, 0],
    scale: [0.7, 1],
    rotateX: [25, 0],
    duration: 900,
    delay: anime.stagger(200),
    easing: 'easeOutBack'
  }, 500);
  
  // Icon glows
  tl.add({
    targets: iconGlows,
    opacity: [0, 0.8],
    scale: [0.5, 1],
    duration: 800,
    delay: anime.stagger(200)
  }, 800);
  
  // Icons pop in with rotation
  tl.add({
    targets: icons,
    scale: [0, 1.2, 1],
    rotate: [-20, 0],
    duration: 700,
    delay: anime.stagger(200),
    easing: 'easeOutElastic(1, .6)'
  }, 900);
  
  // Shine sweep
  tl.add({
    targets: shines,
    translateX: ['-100%', '100%'],
    duration: 800,
    delay: anime.stagger(200),
    easing: 'easeInOutQuad'
  }, 1100);
  
  // Labels
  tl.add({
    targets: labels,
    opacity: [0, 1],
    translateY: [10, 0],
    duration: 600,
    delay: anime.stagger(200)
  }, 1200);
  
  // Descriptions
  if (descs.length > 0) {
    tl.add({
      targets: descs,
      opacity: [0, 1],
      translateY: [10, 0],
      duration: 500,
      delay: anime.stagger(200)
    }, 1400);
  }
  
  // Particles
  tl.add({ targets: particles, opacity: function() { return [0, anime.random(0.3, 0.6)]; }, scale: function() { return [0, 1]; }, duration: 1000, delay: anime.stagger(30) }, 400);

  VidIn._animateParticles(particles, 2500);
  
  // Continuous 3D floating for each card
  iconCards.forEach(function(card, i) {
    var conceptColor = [primaryColor, secondaryColor, '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'][i % 6];
    
    // 3D rotation float
    anime({
      targets: card,
      rotateY: [-8, 8],
      rotateX: [-5, 5],
      duration: 3000 + i * 200,
      delay: 2500 + i * 150,
      direction: 'alternate',
      loop: true,
      easing: 'easeInOutSine'
    });
    
    // Box shadow pulse for depth
    anime({
      targets: card,
      boxShadow: [
        '0 20px 50px ' + conceptColor + '40, inset 0 2px 0 rgba(255,255,255,0.2), inset 0 -2px 0 rgba(0,0,0,0.1)',
        '0 30px 70px ' + conceptColor + '60, inset 0 2px 0 rgba(255,255,255,0.3), inset 0 -2px 0 rgba(0,0,0,0.15)',
        '0 20px 50px ' + conceptColor + '40, inset 0 2px 0 rgba(255,255,255,0.2), inset 0 -2px 0 rgba(0,0,0,0.1)'
      ],
      duration: 3500 + i * 250,
      delay: 3000 + i * 200,
      direction: 'alternate',
      loop: true,
      easing: 'easeInOutSine'
    });
  });
  
  // Whole card subtle float
  conceptCards.forEach(function(card, i) {
    anime({
      targets: card,
      translateY: [-5, 5],
      duration: 2800 + i * 180,
      delay: 2800 + i * 100,
      direction: 'alternate',
      loop: true,
      easing: 'easeInOutSine'
    });
  });

  return tl;
};

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = VidIn;
}
