"use client";

import { Briefcase } from "lucide-react";
import Link from "next/link";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { FormField } from "@/lib/interfaces";
import { Form } from "@/components/ui/form";
import CustomField from "@/components/form-fields/custom-field";
import { useMemo, useState } from "react";
import { Icons } from "@/components/ui/icons";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import Header from "@/components/ui/header";
import { signIn } from "next-auth/react";

type Mode = "login" | "register";
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

/* --------- Campos y esquemas --------- */
const loginFields: FormField[] = [
  {
    name: "email",
    label: "Email",
    placeholder: "example@example.com",
    type: "text",
    validation: z
      .string()
      .email({ message: "Ingresa un email válido" })
      .min(1, { message: "El email es obligatorio" }),
  },
  {
    name: "password",
    label: "Contraseña",
    placeholder: "********",
    type: "password",
    validation: z.string().min(6, {
      message: "La contraseña debe tener al menos 6 caracteres",
    }),
  },
];

const registerFields: FormField[] = [
  ...loginFields,
  {
    name: "confirmPassword",
    label: "Confirmar contraseña",
    placeholder: "********",
    type: "password",
    validation: z.string().min(6, {
      message: "Confirma tu contraseña",
    }),
  },
];

const loginSchema = z.object(
  loginFields.reduce((acc, f) => {
    acc[f.name] = f.validation;
    return acc;
  }, {} as Record<string, z.ZodType>)
);

const registerSchema = z
  .object(
    registerFields.reduce((acc, f) => {
      acc[f.name] = f.validation;
      return acc;
    }, {} as Record<string, z.ZodType>)
  )
  .refine((data) => data.password === data.confirmPassword, {
    path: ["confirmPassword"],
    message: "Las contraseñas no coinciden",
  });

/* --------- Componente de formulario --------- */
function AuthForm({
  mode,
  onModeChange,
}: {
  mode: Mode;
  onModeChange: (m: Mode) => void;
}) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const schema = useMemo(
    () => (mode === "login" ? loginSchema : registerSchema),
    [mode]
  );
  const fields = mode === "login" ? loginFields : registerFields;

  type LoginValues = z.infer<typeof loginSchema>;
  type RegisterValues = z.infer<typeof registerSchema>;
  type FormValues = LoginValues | RegisterValues;

  const form = useForm<FormValues>({
    resolver: zodResolver(schema as any),
    defaultValues:
      mode === "login"
        ? ({ email: "", password: "" } as any)
        : ({ email: "", password: "", confirmPassword: "" } as any),
    mode: "onSubmit",
  });

  const handleSubmit = form.handleSubmit(async (values) => {
    console.log("Submitting form", values);
    //print api url
    console.log("API URL:", API_URL);
    setIsLoading(true);
    try {
      if (mode === "login") {
        // usa NextAuth para que maneje cookies, callbacks y refresh
        const res = await signIn("credentials", {
          email: (values as any).email,
          password: (values as any).password,
          redirect: false,
        });

        if (!res || res.error) {
          // NextAuth suele devolver "CredentialsSignin" cuando la API responde 401
          const msg =
            res?.error === "CredentialsSignin"
              ? "Credenciales inválidas"
              : res?.error || "No se pudo iniciar sesión";
          toast.error(msg);
          return;
        }

        toast.success("Inicio de sesión exitoso");
        router.push("/empresas");
        return;
      }

      // registro
      const registerRes = await fetch(
        `${API_URL}/api/auth/register`, 
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: (values as any).email,
            password: (values as any).password,
          }),
        }
      );

      const payload = await registerRes.json().catch(() => ({} as any));

      if (!registerRes.ok) {
        throw new Error(payload?.message || "No se pudo registrar");
      }

      toast.success("Cuenta creada");

      // auto-login opcional después de registrarse
      const loginRes = await signIn("credentials", {
        email: (values as any).email,
        password: (values as any).password,
        redirect: false,
      });

      if (!loginRes || loginRes.error) {
        // si por políticas prefieres no auto-loguear, cambia esto por onModeChange("login")
        toast.success("Ahora inicia sesión con tu nueva cuenta");
        onModeChange("login");
        return;
      }

      router.push("/empresas");
    } catch (err: any) {
      toast.error(err?.message || "Ocurrió un error");
    } finally {
      setIsLoading(false);
    }
  });



  return (
    <div className="w-full max-w-sm">
      <Form key={mode} {...form}>
        <form className="flex flex-col gap-6 px-4" onSubmit={handleSubmit}>
          <div className="flex flex-col items-center gap-2">
            <Briefcase className="w-8 h-8 text-primary" />
            <h1 className="text-3xl font-bold">
              {mode === "login" ? "Bienvenido de vuelta" : "Crea tu cuenta"}
            </h1>
            <span className="text-xl text-muted-foreground">
              La mejor IA para analizar tu crédito
            </span>

            {mode === "login" ? (
              <div className="text-center text-sm text-muted-foreground">
                ¿No tienes una cuenta?{" "}
                <button
                  type="button"
                  onClick={() => onModeChange("register")}
                  className="underline underline-offset-4 text-primary"
                >
                  Regístrate
                </button>
              </div>
            ) : (
              <div className="text-center text-sm text-muted-foreground">
                ¿Ya tienes cuenta?{" "}
                <button
                  type="button"
                  onClick={() => onModeChange("login")}
                  className="underline underline-offset-4 text-primary"
                >
                  Inicia sesión
                </button>
              </div>
            )}
          </div>

          <div className="flex flex-col gap-2">
            {fields.map((field) => (
              <CustomField
                key={field.name}
                form={form as any}
                fieldInfo={field}
              />
            ))}
          </div>

          <Button type="submit" className="cursor-pointer" disabled={isLoading}>
            {mode === "login" ? "Iniciar sesión" : "Crear cuenta"}
            {isLoading && (
              <Icons.spinner className="animate-spin size-5 ml-2" />
            )}
          </Button>
        </form>
      </Form>
    </div>
  );
}

/* --------- Página --------- */
export default function AuthPage() {
  const [mode, setMode] = useState<Mode>("login");

  return (
    <div>
      <Header />
      <div className="bg-background flex h-[calc(100vh-96px)] flex-col items-center justify-center gap-6 md:p-10">
        <AuthForm mode={mode} onModeChange={setMode} />
      </div>
    </div>
  );
}
