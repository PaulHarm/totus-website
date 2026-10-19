const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync((process.argv[2] || 'dist') + '/motion.js', 'utf8');

function environment(reduced = false) {
  const media = { matches: reduced, listeners: [], addEventListener(_, fn) { this.listeners.push(fn); } };
  const documentEvents = {};
  const windowEvents = {};
  const animations = [];
  class Element {
    constructor() { this.parentElement = null; }
    animate(frames, options) {
      const listeners = {};
      const animation = {
        canceled: false, frames, options,
        addEventListener(type, handler) { listeners[type] = handler; },
        cancel() { this.canceled = true; listeners.cancel?.(); }
      };
      animations.push(animation);
      return animation;
    }
  }
  const context = vm.createContext({
    window: {
      matchMedia: query => query.includes('reduced-motion') ? media : { matches: false },
      addEventListener(type, listener) { windowEvents[type] = listener; },
      scrollY: 0
    },
    document: {
      querySelector: () => null,
      querySelectorAll: () => [],
      addEventListener(type, listener) { documentEvents[type] = listener; }
    },
    location: { pathname: '/index.html' }, Element,
    requestAnimationFrame: fn => fn()
  });
  vm.runInContext(source + '\nthis.testMotion = motion;', context);
  return { motion: context.testMotion, Element, media, animations, documentEvents, windowEvents };
}

let env = environment(true);
assert.equal(env.motion.reveal(new env.Element()), null, 'Reduced motion must not start animations');
assert.equal(env.animations.length, 0);
env = environment();
const target = new env.Element();
const first = env.motion.reveal(target);
assert.equal(first.options.fill, 'backwards', 'No persistent final style may hide content');
const second = env.motion.swap(target);
assert.equal(first.canceled, true, 'Rapid interactions cancel the previous animation');
assert.equal(second.canceled, false);
env.media.matches = true;
env.media.listeners.forEach(fn => fn());
assert.equal(second.canceled, true, 'Changing reduced-motion preference cancels active movement');
assert.equal(env.motion.swap(target), null);
env = environment();
const parent = new env.Element(), child = new env.Element();
child.parentElement = parent;
const entrance = env.motion.reveal(parent);
env.documentEvents.focusin({ target: child });
assert.equal(entrance.canceled, true, 'Keyboard focus immediately reveals its animated ancestor');
const printAnimation = env.motion.reveal(parent);
env.windowEvents.beforeprint();
assert.equal(printAnimation.canceled, true, 'Printing cannot capture an incomplete reveal');
assert.equal(env.motion.animate({}), null, 'Unsupported animation APIs preserve visible content');
console.log('Motion checks passed: reduced preference, rapid interactions, keyboard focus, printing and progressive enhancement.');
