// Spending types
export interface SpendingEntry {
  Item: string
  Cost: number
  Quantity?: number
  Measure?: string
  Location?: string
  Shop?: string
  Details?: string
  Tag?: string
  Date: string
  'Receipt Ref'?: string
  Receipt?: string
  transactionId?: string
  'Sub Sub Category'?: string
  'Sub Category'?: string
  Category?: string
  Latitude?: number
  Longitude?: number
}

export interface SpendingSummary {
  total_cost: number
  transaction_count: number
  latest_transaction_date: string | null
  uncategorized_count: number
  by_category: Record<string, number>
  by_shop: Record<string, number>
  by_tag: Record<string, number>
}

export interface SpendingFilters {
  start_date?: string
  end_date?: string
  tags?: string[]
  shops?: string[]
  locations?: string[]
  categories?: string[]
  sub_categories?: string[]
}

// Income types
export interface IncomeEntry {
  'Gross Income': number
  'Salary Sacrifice': number
  Tax: number
  Income: number
  Date: string
  Employer: string
  Description: string
  Taxable: 'Not-taxable' | 'Taxable' | 'Franked Dividends'
  'Received in bank account': string
  Comment?: string
  'Financial Year'?: string
  'Taxable Income'?: number
}

export interface IncomeSummary {
  total_gross: number
  total_tax: number
  total_net: number
  by_financial_year: Record<string, {
    'Gross Income': number
    Tax: number
    Income: number
    'Taxable Income': number
  }>
  by_employer: Record<string, {
    'Gross Income': number
    Income: number
  }>
}

// Hierarchy types
export interface CategoryEntry {
  'Sub Category': string
  Category: string
}

export interface SubCategoryEntry {
  'Sub Sub Category': string
  'Sub Category': string
}

export interface ItemEntry {
  'All Items': string
  'Sub Sub Category': string
}

export interface HierarchyData {
  categories: CategoryEntry[]
  sub_categories: SubCategoryEntry[]
  items: ItemEntry[]
}

// Location types
export interface LocationEntry {
  Location: string
  Latitude?: number
  Longitude?: number
}

export interface GeocodeResult {
  address: string
  latitude: number
  longitude: number
  display_name: string
}

// Transaction types
export interface Transaction {
  transactionId: string
  Cost: number
  Shop: string
  Date: string
  'Upbank Category'?: string
  'Upbank Text'?: string
  Item?: string
  Location?: string
  Quantity?: number
  Measure?: string
  Details?: string
  Tag?: string
}

// System types
export interface SystemStatus {
  status: string
  timestamp: string
  data_source: string
  counts: {
    spending: number
    income: number
    locations: number
    categories: number
    sub_categories: number
    items: number
  }
  latest_transactions: {
    spending: string | null
    income: string | null
  }
}

// Filter options
export interface FilterOptions {
  tags: string[]
  shops: string[]
  locations: string[]
  categories: string[]
  sub_categories: string[]
  sub_sub_categories: string[]
}

export interface IncomeFilterOptions {
  employers: string[]
  descriptions: string[]
  financial_years: string[]
}
