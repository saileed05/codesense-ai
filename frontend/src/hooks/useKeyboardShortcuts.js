import { useEffect } from 'react';

export const useKeyboardShortcuts = ({
  onPlay,
  onPause,
  onReset,
  onNext,
  onPrevious,
  isExecuting,
  isPaused
}) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl+Space or Space (when not in input/textarea)
      if ((e.ctrlKey && e.code === 'Space') || (e.code === 'Space' && !e.target.matches('input, textarea'))) {
        e.preventDefault();
        if (isPaused || !isExecuting) {
          onPlay();
        } else {
          onPause();
        }
      }
      // Ctrl+Right Arrow
      else if (e.ctrlKey && e.code === 'ArrowRight') {
        e.preventDefault();
        onNext();
      }
      // Ctrl+Left Arrow
      else if (e.ctrlKey && e.code === 'ArrowLeft') {
        e.preventDefault();
        onPrevious();
      }
      // Ctrl+R
      else if (e.ctrlKey && e.code === 'KeyR') {
        e.preventDefault();
        onReset();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onPlay, onPause, onReset, onNext, onPrevious, isExecuting, isPaused]);
};

export default useKeyboardShortcuts;