export type ApiMetadata = { source: string; unit: string; price_type: string; frequency: string }
export type ApiError = { error: { code: string; message_fr?: string; message_ar?: string; message_en?: string } }
export type HealthResponse = { status: string; app: string; environment: string }
