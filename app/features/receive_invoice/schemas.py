from pydantic import BaseModel, Field

class MobilePaymentData(BaseModel):
    issuing_bank: str = Field(description="Nombre del banco desde donde se envía el dinero")
    receiving_bank: str = Field(description="Nombre del banco que recibe el dinero")
    reference: str = Field(description="Número de referencia o confirmación de la transacción (numérico)")
    amount: float = Field(description="Monto de la transacción expresado estrictamente como número flotante")
    date: str = Field(description="Fecha de la transacción en formato DD/MM/AAAA o similar encontrado")