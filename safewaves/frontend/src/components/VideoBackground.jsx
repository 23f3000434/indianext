import { useState } from 'react';

/**
 * VideoBackground - Fixed fullscreen background video with dark overlay.
 *
 * Renders a looping, muted video anchored to the bottom of the viewport,
 * scaled to 120% for a cinematic parallax feel. Falls back to a plain
 * dark background if the video fails to load.
 */
function VideoBackground() {
  const [hasError, setHasError] = useState(false);

  return (
    <>
      {/* Video container -- fixed behind all content */}
      {!hasError && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 0,
            overflow: 'hidden',
            pointerEvents: 'none',
          }}
        >
          <video
            autoPlay
            loop
            muted
            playsInline
            onError={() => setHasError(true)}
            style={{
              width: '120%',
              height: '120%',
              objectFit: 'cover',
              position: 'absolute',
              bottom: 0,
              left: '50%',
              transform: 'translateX(-50%)',
            }}
          >
            <source src="/bg-video.mp4" type="video/mp4" />
          </video>
        </div>
      )}

      {/* Dark overlay */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 0,
          background: hasError
            ? 'rgb(8, 6, 15)'
            : 'linear-gradient(180deg, rgba(8, 6, 15, 0.58) 0%, rgba(8, 6, 15, 0.7) 56%, rgba(8, 6, 15, 0.8) 100%)',
          pointerEvents: 'none',
        }}
      />
    </>
  );
}

export default VideoBackground;
