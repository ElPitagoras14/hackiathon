import { TextField } from "@/lib/interfaces";
import { ControllerRenderProps } from "react-hook-form";
import { FormControl, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import CustomLabel from "@/components/form-fields/custom-label";

interface CustomTextProps {
  fieldInfo: TextField;
  field: ControllerRenderProps;
}

export default function CustomText({ fieldInfo, field }: CustomTextProps) {
  const { label, placeholder, description } = fieldInfo;

  return (
    <>
      <CustomLabel label={label} description={description} />
      <FormControl>
        <Input placeholder={placeholder} {...field} />
      </FormControl>
      <FormMessage />
    </>
  );
}
