import { useCallback, useEffect, useMemo, useRef } from "react";
import { createPortal } from "react-dom";
import { gsap } from "gsap";
import "./TargetCursor.css";

function isMobileDevice() {
  if (typeof window === "undefined") return true;
  return ("ontouchstart" in window && window.innerWidth <= 768) || /android|iphone|ipad|ipod|mobile/i.test(navigator.userAgent);
}

export default function TargetCursor({
  targetSelector = ".cursor-target",
  spinDuration = 2,
  hideDefaultCursor = true,
  hoverDuration = 0.2,
  parallaxOn = true,
  cursorColor = "#ffffff",
  cursorColorOnTarget = "#5ee7f4",
}) {
  const cursorRef = useRef(null);
  const dotRef = useRef(null);
  const cornersRef = useRef([]);
  const spinRef = useRef(null);
  const activeRef = useRef(null);
  const mobile = useMemo(() => isMobileDevice(), []);

  const move = useCallback((x, y) => {
    if (cursorRef.current) gsap.to(cursorRef.current, { x, y, duration: 0.1, ease: "power3.out", overwrite: true });
  }, []);

  useEffect(() => {
    if (mobile || !cursorRef.current) return undefined;
    const cursor = cursorRef.current;
    const corners = cornersRef.current;
    const originalCursor = document.body.style.cursor;
    if (hideDefaultCursor) document.body.style.cursor = "none";
    gsap.set(cursor, { x: innerWidth / 2, y: innerHeight / 2 });
    spinRef.current = gsap.timeline({ repeat: -1 }).to(cursor, { rotation: "+=360", duration: spinDuration, ease: "none" });

    const alignTarget = (target, x, y, duration = hoverDuration) => {
      if (!target) return;
      const rect = target.getBoundingClientRect();
      const positions = [[rect.left - 3, rect.top - 3], [rect.right - 9, rect.top - 3], [rect.right - 9, rect.bottom - 9], [rect.left - 3, rect.bottom - 9]];
      corners.forEach((corner, index) => gsap.to(corner, { x: positions[index][0] - x, y: positions[index][1] - y, duration, ease: "power2.out", overwrite: true }));
    };

    const resetCorners = () => {
      activeRef.current = null;
      spinRef.current?.resume();
      gsap.to(corners, { x: 0, y: 0, borderColor: cursorColor, duration: hoverDuration, overwrite: true });
      gsap.to(dotRef.current, { backgroundColor: cursorColor, duration: hoverDuration });
    };
    const onMove = (event) => {
      move(event.clientX, event.clientY);
      if (activeRef.current) alignTarget(activeRef.current, event.clientX, event.clientY, parallaxOn ? 0.12 : 0);
    };
    const onOver = (event) => {
      const target = event.target.closest?.(targetSelector);
      if (!target || activeRef.current === target) return;
      activeRef.current = target;
      spinRef.current?.pause();
      gsap.set(cursor, { rotation: 0 });
      alignTarget(target, event.clientX, event.clientY);
      gsap.to(corners, { borderColor: cursorColorOnTarget, duration: hoverDuration });
      gsap.to(dotRef.current, { backgroundColor: cursorColorOnTarget, duration: hoverDuration });
    };
    const onDown = () => gsap.to([cursor, dotRef.current], { scale: 0.8, duration: 0.15 });
    const onUp = () => gsap.to([cursor, dotRef.current], { scale: 1, duration: 0.2 });
    const onScroll = () => activeRef.current && alignTarget(activeRef.current, gsap.getProperty(cursor, "x"), gsap.getProperty(cursor, "y"), 0.1);
    const onResize = () => activeRef.current && alignTarget(activeRef.current, gsap.getProperty(cursor, "x"), gsap.getProperty(cursor, "y"), 0.1);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseover", onOver);
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize);
    window.addEventListener("mousedown", onDown);
    window.addEventListener("mouseup", onUp);
    document.body.addEventListener("mouseleave", resetCorners);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseover", onOver);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("mouseup", onUp);
      document.body.removeEventListener("mouseleave", resetCorners);
      spinRef.current?.kill();
      document.body.style.cursor = originalCursor;
    };
  }, [cursorColor, cursorColorOnTarget, hideDefaultCursor, mobile, move, parallaxOn, spinDuration, targetSelector, hoverDuration]);

  if (mobile || typeof document === "undefined") return null;
  return createPortal(<div ref={cursorRef} className="target-cursor-wrapper" aria-hidden="true"><span ref={dotRef} className="target-cursor-dot" style={{ backgroundColor: cursorColor }} />{["tl", "tr", "br", "bl"].map((corner) => <span key={corner} ref={(node) => { if (node) cornersRef.current[["tl", "tr", "br", "bl"].indexOf(corner)] = node; }} className={`target-cursor-corner corner-${corner}`} style={{ borderColor: cursorColor }} />)}</div>, document.body);
}
