import { useState, useMemo } from 'react'
import { Input } from '@/components/ui/input'

interface SearchableFilterListProps {
  title: string
  options: string[]
  selected: string[]
  onChange: (value: string, checked: boolean) => void
  maxHeight?: number
}

export function SearchableFilterList({
  title,
  options,
  selected,
  onChange,
  maxHeight = 160,
}: SearchableFilterListProps) {
  const [search, setSearch] = useState('')

  const filteredOptions = useMemo(() => {
    if (!search.trim()) return options
    const searchLower = search.toLowerCase()
    return options.filter((opt) => opt.toLowerCase().includes(searchLower))
  }, [options, search])

  return (
    <div>
      <h3 className="font-medium mb-2">{title}</h3>
      {options.length > 10 && (
        <Input
          type="text"
          placeholder={`Search ${title.toLowerCase()}...`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="mb-2 h-8 text-sm"
        />
      )}
      <div className="space-y-1 overflow-auto" style={{ maxHeight }}>
        {filteredOptions.length === 0 ? (
          <div className="text-sm text-muted-foreground">No matches</div>
        ) : (
          filteredOptions.map((option) => (
            <label key={option} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={selected.includes(option)}
                onChange={(e) => onChange(option, e.target.checked)}
              />
              {option}
            </label>
          ))
        )}
      </div>
      {selected.length > 0 && (
        <div className="text-xs text-muted-foreground mt-1">
          {selected.length} selected
        </div>
      )}
    </div>
  )
}
