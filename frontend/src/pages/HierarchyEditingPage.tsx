import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, Plus, Trash } from 'lucide-react'
import { LoadingPage } from '@/components/common/LoadingSpinner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  fetchHierarchy,
  updateCategories,
  updateSubCategories,
  updateItems,
} from '@/api/hierarchy'
import type { CategoryEntry, SubCategoryEntry, ItemEntry } from '@/types'

export function HierarchyEditingPage() {
  const queryClient = useQueryClient()

  const { data: hierarchy, isLoading } = useQuery({
    queryKey: ['hierarchy'],
    queryFn: fetchHierarchy,
  })

  const [categories, setCategories] = useState<CategoryEntry[]>([])
  const [subCategories, setSubCategories] = useState<SubCategoryEntry[]>([])
  const [items, setItems] = useState<ItemEntry[]>([])
  const [hasChanges, setHasChanges] = useState({
    categories: false,
    subCategories: false,
    items: false,
  })

  // Initialize state when data loads
  if (hierarchy && categories.length === 0) {
    setCategories(hierarchy.categories)
    setSubCategories(hierarchy.sub_categories)
    setItems(hierarchy.items)
  }

  const saveCategoriesMutation = useMutation({
    mutationFn: () => updateCategories(categories),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hierarchy'] })
      setHasChanges((prev) => ({ ...prev, categories: false }))
    },
  })

  const saveSubCategoriesMutation = useMutation({
    mutationFn: () => updateSubCategories(subCategories),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hierarchy'] })
      setHasChanges((prev) => ({ ...prev, subCategories: false }))
    },
  })

  const saveItemsMutation = useMutation({
    mutationFn: () => updateItems(items),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hierarchy'] })
      setHasChanges((prev) => ({ ...prev, items: false }))
    },
  })

  if (isLoading) return <LoadingPage />

  const handleCategoryChange = (index: number, field: keyof CategoryEntry, value: string) => {
    const updated = [...categories]
    updated[index] = { ...updated[index], [field]: value }
    setCategories(updated)
    setHasChanges((prev) => ({ ...prev, categories: true }))
  }

  const handleSubCategoryChange = (index: number, field: keyof SubCategoryEntry, value: string) => {
    const updated = [...subCategories]
    updated[index] = { ...updated[index], [field]: value }
    setSubCategories(updated)
    setHasChanges((prev) => ({ ...prev, subCategories: true }))
  }

  const handleItemChange = (index: number, field: keyof ItemEntry, value: string) => {
    const updated = [...items]
    updated[index] = { ...updated[index], [field]: value }
    setItems(updated)
    setHasChanges((prev) => ({ ...prev, items: true }))
  }

  const addCategory = () => {
    setCategories([...categories, { 'Sub Category': '', Category: '' }])
    setHasChanges((prev) => ({ ...prev, categories: true }))
  }

  const addSubCategory = () => {
    setSubCategories([...subCategories, { 'Sub Sub Category': '', 'Sub Category': '' }])
    setHasChanges((prev) => ({ ...prev, subCategories: true }))
  }

  const addItem = () => {
    setItems([...items, { 'All Items': '', 'Sub Sub Category': '' }])
    setHasChanges((prev) => ({ ...prev, items: true }))
  }

  const removeCategory = (index: number) => {
    setCategories(categories.filter((_, i) => i !== index))
    setHasChanges((prev) => ({ ...prev, categories: true }))
  }

  const removeSubCategory = (index: number) => {
    setSubCategories(subCategories.filter((_, i) => i !== index))
    setHasChanges((prev) => ({ ...prev, subCategories: true }))
  }

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index))
    setHasChanges((prev) => ({ ...prev, items: true }))
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Hierarchy Editing</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Categories (Top Table) */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Categories</CardTitle>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={addCategory}>
                <Plus className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                onClick={() => saveCategoriesMutation.mutate()}
                disabled={!hasChanges.categories || saveCategoriesMutation.isPending}
              >
                <Save className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-2 max-h-96 overflow-auto">
            {categories.map((cat, index) => (
              <div key={index} className="flex gap-2 items-center">
                <Input
                  value={cat['Sub Category']}
                  onChange={(e) => handleCategoryChange(index, 'Sub Category', e.target.value)}
                  placeholder="Sub Category"
                  className="flex-1"
                />
                <Input
                  value={cat.Category}
                  onChange={(e) => handleCategoryChange(index, 'Category', e.target.value)}
                  placeholder="Category"
                  className="flex-1"
                />
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={() => removeCategory(index)}
                >
                  <Trash className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Sub Categories (Middle Table) */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Sub Categories</CardTitle>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={addSubCategory}>
                <Plus className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                onClick={() => saveSubCategoriesMutation.mutate()}
                disabled={!hasChanges.subCategories || saveSubCategoriesMutation.isPending}
              >
                <Save className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-2 max-h-96 overflow-auto">
            {subCategories.map((subCat, index) => (
              <div key={index} className="flex gap-2 items-center">
                <Input
                  value={subCat['Sub Sub Category']}
                  onChange={(e) => handleSubCategoryChange(index, 'Sub Sub Category', e.target.value)}
                  placeholder="Sub Sub Category"
                  className="flex-1"
                />
                <Input
                  value={subCat['Sub Category']}
                  onChange={(e) => handleSubCategoryChange(index, 'Sub Category', e.target.value)}
                  placeholder="Sub Category"
                  className="flex-1"
                />
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={() => removeSubCategory(index)}
                >
                  <Trash className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Items (Base Table) */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Items</CardTitle>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={addItem}>
                <Plus className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                onClick={() => saveItemsMutation.mutate()}
                disabled={!hasChanges.items || saveItemsMutation.isPending}
              >
                <Save className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-2 max-h-96 overflow-auto">
            {items.map((item, index) => (
              <div key={index} className="flex gap-2 items-center">
                <Input
                  value={item['All Items']}
                  onChange={(e) => handleItemChange(index, 'All Items', e.target.value)}
                  placeholder="Item Name"
                  className="flex-1"
                />
                <Input
                  value={item['Sub Sub Category']}
                  onChange={(e) => handleItemChange(index, 'Sub Sub Category', e.target.value)}
                  placeholder="Sub Sub Category"
                  className="flex-1"
                />
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={() => removeItem(index)}
                >
                  <Trash className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
