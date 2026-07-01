import { useEffect, type ReactNode } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMobile } from '@/hooks/useMobile';

interface ResponsiveModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  className?: string;
}

/**
 * ResponsiveModal
 * - Desktop: centered dialog
 * - Mobile: bottom sheet with gesture-friendly close handle
 */
export function ResponsiveModal({
  open,
  onClose,
  title,
  children,
  className,
}: ResponsiveModalProps) {
  const isMobile = useMobile();

  // Body scroll lock
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  // Close on Escape
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        aria-hidden="true"
        onClick={onClose}
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200"
      />

      {/* Panel */}
      {isMobile ? (
        // Bottom Sheet
        <div
          role="dialog"
          aria-modal="true"
          aria-label={title}
          className={cn(
            'fixed bottom-0 left-0 right-0 z-50',
            'bg-card rounded-t-3xl border-t shadow-2xl',
            'animate-in slide-in-from-bottom duration-300',
            'max-h-[90dvh] flex flex-col',
            className
          )}
        >
          {/* Drag handle */}
          <div className="flex justify-center pt-3 pb-1">
            <div className="h-1 w-10 rounded-full bg-muted-foreground/30" />
          </div>

          {/* Header */}
          {title && (
            <div className="flex items-center justify-between px-5 py-3 border-b">
              <h2 className="font-semibold text-base">{title}</h2>
              <button
                onClick={onClose}
                aria-label="Close"
                className="rounded-lg p-2 hover:bg-muted transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* Body */}
          <div className="flex-1 overflow-y-auto overscroll-contain px-5 py-4">
            {children}
          </div>
        </div>
      ) : (
        // Centered Dialog
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            role="dialog"
            aria-modal="true"
            aria-label={title}
            className={cn(
              'bg-card rounded-2xl border shadow-2xl',
              'animate-in zoom-in-95 fade-in duration-200',
              'w-full max-w-lg max-h-[90dvh] flex flex-col',
              className
            )}
          >
            {/* Header */}
            {title && (
              <div className="flex items-center justify-between px-6 py-4 border-b">
                <h2 className="font-semibold text-base">{title}</h2>
                <button
                  onClick={onClose}
                  aria-label="Close"
                  className="rounded-lg p-2 hover:bg-muted transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}

            {/* Body */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {children}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
