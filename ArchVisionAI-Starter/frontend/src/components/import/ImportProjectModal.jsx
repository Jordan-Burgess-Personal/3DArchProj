import {
    useRef,
    useState,
} from 'react';
import {
    FileArchive,
    Upload,
    X,
} from 'lucide-react';

export default function ImportProjectModal({
    isOpen,
    onClose,
}) {
    const fileInputRef = useRef(null)

    const [
        selectedFile,
        setSelectedFile,
    ] = useState(null)

    const [
        isDragging,
        setIsDragging,
    ] = useState(false)

    if (!isOpen) {
        return null
    }

    function openFilePicker() {
        fileInputRef.current?.click()
    }

    function selectFile(file) {
        if(!file){
            return
        }

        if(!file.name.toLowerCase().endsWith('.zip')){
            console.log('Please select a ZIP file.')
            return
        }

        setSelectedFile(file)
    }

    function handleFileChange(event) {
        const file = event.target.files?.[0]
        
        selectFile(file)
    }

    function handleDragOver(event) {
        event.preventDefault()
        setIsDragging(true)
    }

    function handleDragLeave(event) {
        event.preventDefault()
        setIsDragging(false)
    }

    function handleDrop(event) {
        event.preventDefault()
        setIsDragging(false)

        const file = event.dataTransfer.files?.[0]

        selectFile(file)
    }

    function handleClose() {
        setSelectedFile(null)
        setIsDragging(false)
        onClose()
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) {
            return `${bytes} bytes`
        }

        if(bytes < 1024 * 1024) {
            return `${(bytes / 1024).toFixed(2)} KB`
        }

        return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
    }

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
            onMouseDown={(event) => {
                if (event.target === event.currentTarget) {
                    handleClose()
                }
            }}
        >
            <div className="w-full max-w-xl rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl">
             <div className="flex items-start justify-between border-b border-slate-700 px-6 py-5">
                <div>
                    <h2 className="text-xl font-semibold text-white">
                        Import Project
                    </h2>

                    <p className="mt-1 text-sm text-slate-400">
                        Upload an existing ArchVision project.
                    </p>
                </div>

                <button
                    type="button"
                    onClick={handleClose}
                    className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-white"
                    aria-label="Close import project"
                >
                    <X size={20} />
                </button>
             </div>

             <div className="p-6">
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".zip,application/zip"
                    className="hidden"
                    onChange={handleFileChange}
                />

                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={[
                        'flex min-h-64 flex-col',
                        'items-center justify-center',
                        'rounded-lg border-2 border-dashed',
                        'p-8 text-center transition',
                        isDragging
                            ? [
                                'border-indigo-400',
                                'bg-indigo-500/10',
                              ].join(' ')
                            : [
                                'border-slate-600',
                                'bg-slate-950/40',
                                'hover:border-slate-500',
                              ].join(' ')
                    ].join(' ')}
                >
                    <span className="flex h-14 w-14 items-center justify-center rounded-full bg-indigo-500/15 text-indigo-300">
                        <Upload size={28} />
                    </span>

                    <h3 className="mt-4 text-lg font-semibold text-white">
                        Drag and drop your project
                    </h3>

                    <p className="mt-2 text-sm text-slate-400">
                        Drop a ZIP file here or browse your computer.
                    </p>

                    <button
                        type="button"
                        onClick={openFilePicker}
                        className="mt-5 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-500"
                    >
                        Browse Files
                    </button>
                </div>

                {selectedFile && (
                    <div className="mt-5 flex items-center gap-4 rounded-xl border border-slate-700 bg-slate-800/60 p-4">
                        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-indigo-500/15 text-indigo-300">
                            <FileArchive size={22} />
                        </span>

                        <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-medium text-white">
                                {selectedFile.name}
                            </p>

                            <p className="mt-1 truncate text-sm text-slate-400">
                                {formatFileSize(
                                    selectedFile.size,
                                )}
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={() =>
                                setSelectedFile(null)
                            }
                            className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-700 hover:text-white"
                            aria-label="Remove selected file"
                        >
                            <X size={18} />
                        </button>
                    </div>
                )}
            </div>

            <div className="flex justify-end gap-3 border-t border-slate-700 px-6 py-4">
                <button
                    type="button"
                    onClick={handleClose}
                    className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-800 hover:text-white"
                >
                    Cancel
                </button>

                <button
                    type="button"
                    disabled={!selectedFile}
                    onClick={() => {
                        console.log(
                            'Ready to import:',
                            selectedFile,
                        )
                    }}
                    className={[
                        'rounded-lg px-4 py-2',
                        'text-sm font-medium',
                        'transition',
                        selectedFile
                            ? [
                                'bg-indigo-600',
                                'text-white',
                                'hover:bg-indigo-500',
                              ].join(' ')
                            : [
                                'cursor-not-allowed',
                                'bg-slate-700',
                                'text-slate-400',
                              ].join(' '),
                    ].join(' ')}
                >
                    Import Project
                </button>
            </div>
        </div>
    </div>
    )
}