import { Link, useLocation } from 'react-router-dom'
import { Gauge, Activity, MapPin, BarChart3, Users, Sparkles } from 'lucide-react'
import banquePopulaireLogo from '../../assets/nvlogobp.jpg'

const navItems = [
  { label: 'Tableau de bord', path: '/', icon: Gauge },
  { label: 'Analyse incidents', path: '/incidents', icon: Activity },
  { label: 'Analyse RGPH', path: '/demographics', icon: Users },
  { label: 'Carte interactive', path: '/map', icon: MapPin },
  { label: 'Prédiction IA', path: '/predictions', icon: Sparkles },
  { label: 'Recommandations', path: '/recommendations', icon: BarChart3 }
]

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

function Sidebar({ isOpen, onClose }: SidebarProps) {
  const location = useLocation()

  return (
    <>
      {isOpen && (
        <button
          type="button"
          aria-label="Masquer la navigation"
          className="fixed inset-0 z-20 bg-slate-900/30 md:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-30 flex w-72 flex-col overflow-hidden bg-white shadow-soft transition-all duration-300 ease-in-out md:sticky md:top-0 md:h-screen md:shrink-0 ${
          isOpen ? 'translate-x-0 md:w-72 md:opacity-100' : '-translate-x-full md:w-0 md:opacity-0'
        }`}
      >
        <div className="h-32 w-72 border-r border-orange-100 bg-white px-3">
          <div className="flex h-full items-center justify-center">
            <img
              src={banquePopulaireLogo}
              alt="Logo Banque Populaire"
              className="h-28 w-[258px] object-contain"
            />
            <span className="sr-only">Banque Populaire</span>
          </div>
        </div>
        <div className="w-72 flex-1 bg-[linear-gradient(180deg,#FF7A1A_0%,#F05A00_45%,#D94A00_100%)] px-4 py-8 text-white">
          <div className="px-2 text-sm font-semibold text-gray-200">Maintenance prédictive des GAB</div>
          <nav className="mt-8 space-y-2">
            {navItems.map((item) => {
              const active = location.pathname === item.path
              const Icon = item.icon
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => {
                    if (window.matchMedia('(max-width: 767px)').matches) {
                      onClose()
                    }
                  }}
                  className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                    active ? 'border border-[#FDBA74] bg-[#FB923C] text-white shadow-lg' : 'text-white/95 hover:bg-[#FFF1E8]/15 hover:text-white'
                  }`}
                >
                  <Icon size={18} />
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </div>
      </aside>
    </>
  )
}

export default Sidebar
