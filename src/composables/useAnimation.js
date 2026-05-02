import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function useAnimation() {
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /**
   * Default entrance animation for elements
   */
  const entrance = (target, options = {}) => {
    if (prefersReducedMotion) return;
    
    return gsap.from(target, {
      y: 20,
      duration: 0.8,
      stagger: 0.1,
      ease: 'power3.out',
      ...options
    });
  };

  /**
   * Staggered list animation
   */
  const staggerList = (target, options = {}) => {
    if (prefersReducedMotion) return;
    
    return gsap.from(target, {
      x: -20,
      duration: 0.6,
      stagger: 0.05,
      ease: 'power2.out',
      ...options
    });
  };

  /**
   * Magnetic hover effect
   */
  const magneticHover = (el, strength = 0.5) => {
    if (prefersReducedMotion || !el) return;

    el.addEventListener('mousemove', (e) => {
      const { left, top, width, height } = el.getBoundingClientRect();
      const x = e.clientX - (left + width / 2);
      const y = e.clientY - (top + height / 2);
      
      gsap.to(el, {
        x: x * strength,
        y: y * strength,
        duration: 0.3,
        ease: 'power2.out'
      });
    });

    el.addEventListener('mouseleave', () => {
      gsap.to(el, {
        x: 0,
        y: 0,
        duration: 0.5,
        ease: 'elastic.out(1, 0.3)'
      });
    });
  };

  /**
   * Typewriter effect for text
   */
  const typewriter = (target, text, onComplete = null) => {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) return;

    el.textContent = '';
    const chars = text.split('');
    const tl = gsap.timeline({ onComplete });
    
    chars.forEach((char) => {
      tl.to(el, {
        duration: 0.03,
        text: el.textContent + char,
        ease: 'none'
      }, '+=0.02');
    });
    
    return tl;
  };

  /**
   * Word-by-word reveal
   */
  const wordReveal = (target) => {
    if (prefersReducedMotion) return;
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) return;

    const text = el.textContent;
    el.innerHTML = text.split(' ').map(word => `<span class="word" style="display:inline-block; white-space:pre;">${word} </span>`).join('');
    
    return gsap.from(el.querySelectorAll('.word'), {
      y: 10,
      duration: 0.4,
      stagger: 0.03,
      ease: 'power2.out'
    });
  };

  /**
   * Scroll triggered reveal
   */
  const scrollReveal = (target, options = {}) => {
    if (prefersReducedMotion) return;

    gsap.from(target, {
      scrollTrigger: {
        trigger: target,
        start: 'top 85%',
        toggleActions: 'play none none reverse'
      },
      y: 30,
      duration: 1,
      ease: 'power3.out',
      ...options
    });
  };

  return {
    entrance,
    staggerList,
    magneticHover,
    typewriter,
    wordReveal,
    scrollReveal,
    gsap
  };
}
