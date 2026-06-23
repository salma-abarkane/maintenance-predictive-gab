import { useEffect, useMemo, useState, type ChangeEvent } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet'
import { UploadCloud } from 'lucide-react'
import * as XLSX from 'xlsx'
import 'leaflet/dist/leaflet.css'
import SectionHeader from '../components/ui/SectionHeader'
import FilterSelect from '../components/ui/FilterSelect'
import { formatDh, formatNumber, inferBankingActivityFromText } from '../data/bankingActivity'

const DEFAULT_CENTER: [number, number] = [33.97, -6.85]

interface AgencyGpsPoint {
  codeAgence: string
  nomAgence: string
  adresse: string
  telephone: string
  gsm: string
  latitude: number
  longitude: number
}

function agencyFilterKey(agency: AgencyGpsPoint) {
  return `${agency.codeAgence || 'Sans code'} — ${agency.nomAgence || 'Agence sans nom'}`
}

function normalizeColumn(value: string) {
  return value.trim().toLowerCase().replace(/[\s_-]/g, '')
}

function cellToString(value: unknown) {
  if (value === null || value === undefined) {
    return ''
  }
  return String(value).trim()
}

function parseCoordinate(value: unknown) {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null
  }
  const parsed = Number(String(value ?? '').replace(',', '.').trim())
  return Number.isFinite(parsed) ? parsed : null
}

async function readAgencyGpsFile(file: File): Promise<AgencyGpsPoint[]> {
  const buffer = await file.arrayBuffer()
  const workbook = XLSX.read(buffer, { type: 'array' })
  const sheetName = workbook.SheetNames[0]
  if (!sheetName) {
    throw new Error('Le fichier Excel ne contient aucune feuille.')
  }

  const worksheet = workbook.Sheets[sheetName]
  const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(worksheet, { defval: '' })
  const columns = Object.keys(rows[0] ?? {}).reduce<Record<string, string>>((acc, column) => {
    acc[normalizeColumn(column)] = column
    return acc
  }, {})

  const latitudeColumn = columns.latitude
  const longitudeColumn = columns.longitude
  if (!latitudeColumn || !longitudeColumn) {
    throw new Error('Le fichier GPS doit contenir les colonnes Latitude et Longitude.')
  }

  const getColumn = (name: string) => columns[normalizeColumn(name)]
  const codeColumn = getColumn('CODE AGENCE')
  const nameColumn = getColumn('NOM AGENCE')
  const addressColumn = getColumn('ADRESSE')
  const phoneColumn = getColumn('TELEPHONE')
  const gsmColumn = getColumn('GSM')

  const agencies = rows.reduce<AgencyGpsPoint[]>((acc, row) => {
    const latitude = parseCoordinate(row[latitudeColumn])
    const longitude = parseCoordinate(row[longitudeColumn])
    if (latitude === null || longitude === null) {
      return acc
    }

    acc.push({
      codeAgence: cellToString(codeColumn ? row[codeColumn] : ''),
      nomAgence: cellToString(nameColumn ? row[nameColumn] : ''),
      adresse: cellToString(addressColumn ? row[addressColumn] : ''),
      telephone: cellToString(phoneColumn ? row[phoneColumn] : ''),
      gsm: cellToString(gsmColumn ? row[gsmColumn] : ''),
      latitude,
      longitude
    })
    return acc
  }, [])

  if (agencies.length === 0) {
    throw new Error('Aucune agence avec Latitude et Longitude valides n’a été trouvée.')
  }

  return agencies
}

function MapRecenter({ center }: { center: [number, number] }) {
  const map = useMap()
  useEffect(() => {
    map.setView(center, map.getZoom())
  }, [center, map])
  return null
}

function InteractiveMap() {
  const [agencies, setAgencies] = useState<AgencyGpsPoint[]>([])
  const [filterAgency, setFilterAgency] = useState('Toutes')
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const agencyOptions = useMemo(
    () => ['Toutes', ...Array.from(new Set(agencies.map(agencyFilterKey)))],
    [agencies]
  )

  const filteredAgencies = useMemo(
    () => (filterAgency === 'Toutes' ? agencies : agencies.filter((agency) => agencyFilterKey(agency) === filterAgency)),
    [agencies, filterAgency]
  )

  const center = useMemo<[number, number]>(() => {
    const firstAgency = filteredAgencies[0] ?? agencies[0]
    return firstAgency ? [firstAgency.latitude, firstAgency.longitude] : DEFAULT_CENTER
  }, [agencies, filteredAgencies])

  const handleGpsUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) {
      return
    }

    setUploading(true)
    setError(null)
    setMessage(null)
    readAgencyGpsFile(file)
      .then((items) => {
        setAgencies(items)
        setFilterAgency('Toutes')
        setMessage(`Fichier GPS importé avec succès : ${items.length} agences affichées.`)
      })
      .catch((error) => {
        setError((error as Error).message || 'Impossible d’importer le fichier GPS des agences.')
      })
      .finally(() => {
        setUploading(false)
        event.target.value = ''
      })
  }

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Carte interactive"
        description="Visualisez les agences Banque Populaire à partir des coordonnées GPS importées depuis un fichier Excel."
      />

      <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-bporange-500">Importer fichier GPS des agences</p>
            <p className="mt-2 text-sm text-slate-600">
              Le fichier doit contenir les colonnes Latitude et Longitude. Les lignes sans coordonnées sont ignorées automatiquement.
            </p>
          </div>
          <label className="inline-flex cursor-pointer items-center justify-center rounded-3xl bg-[#FFF1E8] px-5 py-3 text-sm font-semibold text-[#F05A00] shadow-soft transition duration-200 hover:bg-[#FFE4D1] hover:text-[#F05A00]">
            <UploadCloud size={18} className="mr-2 text-[#F05A00]" />
            {uploading ? 'Import en cours...' : 'Importer Excel'}
            <input type="file" accept=".xlsx,.xls" className="hidden" onChange={handleGpsUpload} disabled={uploading} />
          </label>
        </div>
        {message && <p className="mt-4 rounded-3xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</p>}
        {error && <p className="mt-4 rounded-3xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.6fr_0.9fr]">
        <div className="relative overflow-hidden rounded-[26px] border border-slate-200/80 bg-white p-0 shadow-soft">
          <MapContainer center={center} zoom={8} scrollWheelZoom className="h-[620px] w-full">
            <MapRecenter center={center} />
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {filteredAgencies.map((agency) => (
              <CircleMarker
                key={`${agency.codeAgence}-${agency.latitude}-${agency.longitude}`}
                center={[agency.latitude, agency.longitude]}
                radius={8}
                pathOptions={{
                  color: '#F05A00',
                  fillColor: '#F05A00',
                  fillOpacity: 0.72,
                  weight: 2
                }}
              >
                <Popup>
                  <div className="space-y-1 text-slate-700">
                    <p className="font-semibold text-slate-900">{agency.nomAgence || 'Agence Banque Populaire'}</p>
                    <p><strong>Code agence:</strong> {agency.codeAgence || '-'}</p>
                    <p><strong>Adresse:</strong> {agency.adresse || '-'}</p>
                    <p><strong>Téléphone:</strong> {agency.telephone || '-'}</p>
                    <p><strong>GSM:</strong> {agency.gsm || '-'}</p>
                    <p><strong>Latitude:</strong> {agency.latitude}</p>
                    <p><strong>Longitude:</strong> {agency.longitude}</p>
                    {(() => {
                      const activity = inferBankingActivityFromText(agency.nomAgence, agency.adresse)
                      return (
                        <>
                          <p><strong>Opérations mensuelles estimées:</strong> {activity ? formatNumber(activity.monthlyOperations) : '-'}</p>
                          <p><strong>Consommation mensuelle estimée:</strong> {activity ? formatDh(activity.monthlyConsumptionDh) : '-'}</p>
                        </>
                      )
                    })()}
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
          {agencies.length === 0 && (
            <div className="pointer-events-none absolute inset-x-6 bottom-6 rounded-[26px] border border-orange-100 bg-white/95 p-5 text-sm text-slate-600 shadow-soft">
              Importez le fichier Excel GPS des agences pour afficher les points sur la carte.
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
            <h3 className="text-lg font-semibold text-bporange-500">Filtrer par agence</h3>
            <p className="mt-2 text-slate-600">Sélectionnez une agence pour recentrer la carte sur son point GPS.</p>
            <div className="mt-6">
              <FilterSelect label="Agence" options={agencyOptions} value={filterAgency} onChange={setFilterAgency} />
            </div>
          </div>

          <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
            <h3 className="text-lg font-semibold text-bporange-500">Agences affichées</h3>
            <p className="mt-4 text-4xl font-semibold text-slate-900">{filteredAgencies.length}</p>
            <p className="mt-3 text-sm text-slate-600">Points GPS visibles sur la carte après import et filtrage.</p>
          </div>

          <div className="rounded-[26px] border border-slate-200/80 bg-white p-6 shadow-soft">
            <h3 className="text-lg font-semibold text-bporange-500">Informations</h3>
            <p className="mt-2 text-slate-600">
              Chaque point correspond à une agence. Cliquez sur un marqueur pour afficher le code, l’adresse, le téléphone, le GSM et les coordonnées GPS.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default InteractiveMap
