import { useEffect, useMemo, useRef, useState } from 'react'
import { Menu, BellRing } from 'lucide-react'
import { api } from '../../services/api'
import { TopCriticalATM } from '../../types/api'

interface NavbarProps {
  onToggleSidebar: () => void
}

function Navbar({ onToggleSidebar }: NavbarProps) {
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [criticalAtms, setCriticalAtms] = useState<TopCriticalATM[]>([])
  const [loadingNotifications, setLoadingNotifications] = useState(true)
  const [notificationError, setNotificationError] = useState<string | null>(null)
  const notificationRef = useRef<HTMLDivElement | null>(null)

  const alerts = useMemo(
    () => criticalAtms.filter((item) => item.riskCategory === 'Critique' || item.riskCategory === 'Élevé'),
    [criticalAtms]
  )

  useEffect(() => {
    let mounted = true
    api.getTopCriticalAtms(5)
      .then((data) => {
        if (mounted) {
          setCriticalAtms(data)
          setNotificationError(null)
        }
      })
      .catch((error) => {
        if (mounted) {
          setNotificationError((error as Error).message || 'Notifications indisponibles.')
        }
      })
      .finally(() => {
        if (mounted) {
          setLoadingNotifications(false)
        }
      })

    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    if (!notificationsOpen) {
      return
    }

    const handlePointerDown = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setNotificationsOpen(false)
      }
    }

    document.addEventListener('mousedown', handlePointerDown)
    return () => document.removeEventListener('mousedown', handlePointerDown)
  }, [notificationsOpen])

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-slate-50/95 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-4">
          <button
            type="button"
            aria-label="Afficher ou masquer la navigation"
            onClick={onToggleSidebar}
            className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-orange-100 bg-white text-bporange-500 shadow-soft transition hover:bg-bporange-50"
          >
            <Menu size={20} className="text-[#F97316]" />
          </button>
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-bporange-600">Système intelligent</p>
            <h1 className="text-xl font-semibold text-slate-900">Tableau de bord de maintenance prédictive</h1>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div ref={notificationRef} className="relative">
            <button
              type="button"
              aria-label="Afficher les notifications"
              aria-expanded={notificationsOpen}
              onClick={() => setNotificationsOpen((open) => !open)}
              className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-[#F05A00] text-white shadow-soft transition hover:bg-[#FF7A1A]"
            >
              <BellRing size={18} />
            </button>
            {alerts.length > 0 && (
              <span className="absolute -right-1 -top-1 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-rose-600 px-1.5 text-[11px] font-bold leading-none text-white shadow-soft">
                {alerts.length}
              </span>
            )}
            <div
              className={`absolute right-0 mt-3 w-80 origin-top-right rounded-3xl border border-orange-100 bg-white p-4 text-left shadow-soft transition duration-200 ${
                notificationsOpen
                  ? 'pointer-events-auto translate-y-0 scale-100 opacity-100'
                  : 'pointer-events-none -translate-y-2 scale-95 opacity-0'
              }`}
            >
              <div className="mb-3">
                <p className="text-sm font-semibold text-slate-900">Alertes GAB critiques</p>
                <p className="text-xs text-slate-500">Alertes issues des scores IA réels.</p>
              </div>
              {loadingNotifications && (
                <p className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">Chargement des notifications...</p>
              )}
              {!loadingNotifications && notificationError && (
                <p className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{notificationError}</p>
              )}
              {!loadingNotifications && !notificationError && alerts.length === 0 && (
                <p className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">Aucune alerte critique disponible.</p>
              )}
              {!loadingNotifications && !notificationError && alerts.length > 0 && (
                <div className="max-h-96 space-y-2 overflow-y-auto pr-1">
                  {alerts.map((item) => (
                    <div key={item.atm} className="rounded-2xl bg-slate-50 px-4 py-3">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold text-slate-900">GAB {item.atm}</p>
                          <p className="mt-1 text-xs text-slate-500">{item.agency} · {item.city}</p>
                        </div>
                        <span className="rounded-full bg-rose-100 px-2 py-1 text-xs font-semibold text-rose-700">
                          {item.riskCategory}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-600">Probabilité de panne : {item.failureProbability.toFixed(1)}%</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Navbar
