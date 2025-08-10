import z from "zod";

interface FieldBase {
  name: string;
  label: string;
  placeholder?: string;
  description?: string;
  type: "text" | "number" | "password";
}

export interface TextField extends FieldBase {
  type: "text";
}

export interface NumberField extends FieldBase {
  type: "number";
}

export interface PasswordField extends FieldBase {
  type: "password";
}

export type FieldInfo = TextField | NumberField | PasswordField;

export interface FormField extends FieldBase {
  validation: z.ZodType;
}
