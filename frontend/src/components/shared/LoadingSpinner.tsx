function LoadingSpinner() {
  return (
    <div className="flex min-h-[240px] items-center justify-center rounded-[26px] border border-slate-200/80 bg-white shadow-soft">
      <div className="inline-flex h-12 w-12 animate-spin items-center justify-center rounded-full border-4 border-bporange-500 border-t-transparent"></div>
    </div>
  )
}

export default LoadingSpinner
