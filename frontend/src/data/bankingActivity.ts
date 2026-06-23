export interface BankingActivityCity {
  city: string
  monthlyOperations: number
  monthlyConsumptionDh: number
  estimatedGabCount: number
}

export const BANKING_ACTIVITY_BY_CITY: BankingActivityCity[] = [
  { city: 'Salé', monthlyOperations: 10000, monthlyConsumptionDh: 10000000, estimatedGabCount: 42 },
  { city: 'Kénitra', monthlyOperations: 10000, monthlyConsumptionDh: 10000000, estimatedGabCount: 44 },
  { city: 'Témara', monthlyOperations: 10000, monthlyConsumptionDh: 10000000, estimatedGabCount: 31 },
  { city: 'Rabat', monthlyOperations: 5000, monthlyConsumptionDh: 6000000, estimatedGabCount: 56 },
  { city: 'Khémisset', monthlyOperations: 5000, monthlyConsumptionDh: 4000000, estimatedGabCount: 22 },
  { city: 'Sidi Kacem', monthlyOperations: 5000, monthlyConsumptionDh: 5000000, estimatedGabCount: 18 },
  { city: 'Sidi Slimane', monthlyOperations: 5000, monthlyConsumptionDh: 4500000, estimatedGabCount: 17 },
  { city: 'Ouezzane', monthlyOperations: 5000, monthlyConsumptionDh: 3000000, estimatedGabCount: 14 },
  { city: 'Sala Al Jadida', monthlyOperations: 5000, monthlyConsumptionDh: 5500000, estimatedGabCount: 16 }
]

export const TOTAL_MONTHLY_OPERATIONS = BANKING_ACTIVITY_BY_CITY.reduce(
  (sum, item) => sum + item.monthlyOperations,
  0
)

export const TOTAL_MONTHLY_CONSUMPTION_DH = BANKING_ACTIVITY_BY_CITY.reduce(
  (sum, item) => sum + item.monthlyConsumptionDh,
  0
)

export const MOST_ACTIVE_CITY = [...BANKING_ACTIVITY_BY_CITY].sort(
  (left, right) => right.monthlyOperations - left.monthlyOperations
)[0]

export function formatNumber(value: number) {
  return value.toLocaleString('fr-FR')
}

export function formatDh(value: number) {
  return `${value.toLocaleString('fr-FR')} DH`
}

export function normalizeCity(value: string) {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
}

const activityByNormalizedCity = new Map(
  BANKING_ACTIVITY_BY_CITY.flatMap((item) => {
    const aliases = [item.city]
    if (item.city === 'Salé') aliases.push('Sale')
    if (item.city === 'Kénitra') aliases.push('Kenitra')
    if (item.city === 'Témara') aliases.push('Temara')
    return aliases.map((alias) => [normalizeCity(alias), item] as const)
  })
)

export function getBankingActivityForCity(city: string) {
  return activityByNormalizedCity.get(normalizeCity(city)) ?? null
}

export function inferBankingActivityFromText(...values: string[]) {
  const normalizedText = normalizeCity(values.filter(Boolean).join(' '))
  return BANKING_ACTIVITY_BY_CITY.find((item) => normalizedText.includes(normalizeCity(item.city))) ?? null
}
