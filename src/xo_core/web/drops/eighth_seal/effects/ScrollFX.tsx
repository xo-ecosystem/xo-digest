import { useEffect, useRef } from "react";

export default function ScrollFX() {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (!scrollRef.current) return;
      const { top } = scrollRef.current.getBoundingClientRect();
      const opacity = Math.max(0, 1 - top / window.innerHeight);
      scrollRef.current.style.opacity = `${opacity}`;
      scrollRef.current.style.transform = `translateY(${top * 0.1}px)`;
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div
      ref={scrollRef}
      className="transition-opacity duration-500 ease-out text-center py-4"
    >
      <div className="inline-block animate-pulse text-xl font-semibold text-[#FFD700]">
        ✨ Scroll to discover the story... ✨
      </div>
    </div>
  );
}
