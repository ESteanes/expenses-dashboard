import { apiClient } from './client'

export function getReceiptUrl(receiptRef: string): string {
  return `${apiClient.defaults.baseURL}/receipts/${encodeURIComponent(receiptRef)}`
}

export async function getReceiptBase64(receiptRef: string): Promise<string[]> {
  const response = await apiClient.get<{ images: string[] }>(
    `/receipts/${encodeURIComponent(receiptRef)}/base64`
  )
  return response.data.images
}

export async function uploadReceipt(
  file: File,
  receiptDate: string,
  existingRef?: string
): Promise<string> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('receipt_date', receiptDate)
  if (existingRef) {
    formData.append('existing_ref', existingRef)
  }

  const response = await apiClient.post<{ receipt_ref: string }>('/receipts', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data.receipt_ref
}

export async function rotateReceipt(receiptRef: string, angle: number): Promise<void> {
  await apiClient.post(`/receipts/${encodeURIComponent(receiptRef)}/rotate`, null, {
    params: { angle },
  })
}

export async function deleteReceipt(receiptRef: string): Promise<void> {
  await apiClient.delete(`/receipts/${encodeURIComponent(receiptRef)}`)
}
