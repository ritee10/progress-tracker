import { useState } from 'react';
import { usePdf } from '@/hooks/usePdf';
import { LoadingOverlay } from '@/components/ui/api-status/LoadingOverlay';
import { UploadCloud, File as FileIcon, Save, Layers, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function PdfPage() {
  const [file, setFile] = useState<File | null>(null);
  const [pdfId, setPdfId] = useState<string | null>(null);
  const [hierarchy, setHierarchy] = useState<any | null>(null);

  const { uploadPdf, extractHierarchy, saveHierarchy, isUploading, isExtracting, isSaving } =
    usePdf();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    try {
      const res = await uploadPdf(file);
      setPdfId(res.data?.id || res.id);
    } catch {}
  };

  const handleExtract = async () => {
    if (!pdfId) return;
    try {
      const res = await extractHierarchy(pdfId);
      setHierarchy(res.data);
    } catch {}
  };

  const handleSave = async () => {
    if (!hierarchy) return;
    try {
      await saveHierarchy(hierarchy);
      setHierarchy(null);
      setFile(null);
      setPdfId(null);
    } catch {}
  };

  const isBusy = isUploading || isExtracting || isSaving;

  return (
    <div className="space-y-5 sm:space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">PDF Import</h1>
        <p className="text-muted-foreground mt-1 text-sm sm:text-base">
          Upload a PDF to automatically extract learning topics and skills.
        </p>
      </div>

      {/* Workflow progress indicator (mobile-friendly) */}
      <div className="flex items-center gap-3 text-sm">
        <StepIndicator step={1} active={!pdfId} done={!!pdfId} label="Upload" />
        <div className="flex-1 h-px bg-border" />
        <StepIndicator step={2} active={!!pdfId && !hierarchy} done={!!hierarchy} label="Extract" />
        <div className="flex-1 h-px bg-border" />
        <StepIndicator step={3} active={!!hierarchy} done={false} label="Save" />
      </div>

      {/* Main workflow — stack on mobile, 2-col on md+ */}
      <div className="grid gap-4 sm:gap-6 md:grid-cols-2 relative">
        {isBusy && (
          <LoadingOverlay
            message={
              isUploading ? 'Uploading PDF...' : isExtracting ? 'Extracting hierarchy...' : 'Saving...'
            }
          />
        )}

        {/* ── Step 1: Upload ── */}
        <div className="border rounded-2xl p-5 sm:p-6 bg-card flex flex-col gap-4">
          <h2 className="font-semibold text-base flex items-center gap-2">
            <UploadCloud className="h-5 w-5 text-primary shrink-0" />
            1. Upload Document
          </h2>

          <label
            htmlFor="pdf-upload"
            className={cn(
              'border-2 border-dashed rounded-xl p-6 sm:p-8 flex flex-col items-center justify-center text-center cursor-pointer',
              'hover:bg-muted/50 active:bg-muted transition-colors',
              'focus-within:ring-2 focus-within:ring-ring'
            )}
          >
            <FileIcon className="h-10 w-10 text-muted-foreground mb-3" />
            <span className="text-sm font-medium text-primary underline-offset-2">
              {file ? file.name : 'Tap to choose a PDF'}
            </span>
            {!file && (
              <span className="text-xs text-muted-foreground mt-1">PDF files only</span>
            )}
            <input
              type="file"
              accept=".pdf"
              className="sr-only"
              id="pdf-upload"
              onChange={handleFileChange}
            />
          </label>

          <button
            disabled={!file || !!pdfId}
            onClick={handleUpload}
            className="w-full bg-primary text-primary-foreground px-4 py-3 rounded-xl font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 active:scale-[0.98] transition-all min-h-[44px]"
          >
            {pdfId ? '✓ Uploaded' : 'Upload PDF'}
          </button>
        </div>

        {/* ── Step 2 & 3: Extract & Save ── */}
        <div className="border rounded-2xl p-5 sm:p-6 bg-card flex flex-col gap-4">
          <h2 className="font-semibold text-base flex items-center gap-2">
            <Layers className="h-5 w-5 text-primary shrink-0" />
            2. Extract &amp; Review
          </h2>

          {!hierarchy ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 py-6">
              <p className="text-muted-foreground text-sm">
                {pdfId
                  ? 'Document uploaded. Ready to extract topics.'
                  : 'Upload a document first to begin extraction.'}
              </p>
              <button
                disabled={!pdfId}
                onClick={handleExtract}
                className="border rounded-xl px-4 py-3 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-muted active:scale-[0.98] transition-all min-h-[44px]"
              >
                Extract Hierarchy
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-4 flex-1">
              <div className="border rounded-xl p-4 overflow-auto max-h-[280px] sm:max-h-[300px] bg-muted/30 text-xs">
                <pre className="whitespace-pre-wrap break-words">
                  {JSON.stringify(hierarchy, null, 2)}
                </pre>
              </div>
              <button
                onClick={handleSave}
                className="w-full flex items-center justify-center gap-2 bg-emerald-600 text-white px-4 py-3 rounded-xl font-medium text-sm hover:bg-emerald-700 active:scale-[0.98] transition-all min-h-[44px]"
              >
                <Save className="h-4 w-4" />
                Save to My Skills
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StepIndicator({
  step,
  active,
  done,
  label,
}: {
  step: number;
  active: boolean;
  done: boolean;
  label: string;
}) {
  return (
    <div className="flex flex-col items-center gap-1 shrink-0">
      <div
        className={cn(
          'h-7 w-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors',
          done
            ? 'bg-emerald-500 text-white'
            : active
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-muted-foreground'
        )}
      >
        {done ? <CheckCircle2 className="h-4 w-4" /> : step}
      </div>
      <span className="text-[10px] font-medium text-muted-foreground">{label}</span>
    </div>
  );
}
