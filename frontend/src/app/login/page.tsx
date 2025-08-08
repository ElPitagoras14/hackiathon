"use client";

import { TelescopeIcon } from "lucide-react";
import Link from "next/link";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { FormField } from "@/lib/interfaces";
import { Form } from "@/components/ui/form";
import { SiGithub, SiBuymeacoffee } from "@icons-pack/react-simple-icons";
import CustomField from "@/components/form-fields/custom-field";
import { useState } from "react";
import { signIn } from "next-auth/react";
import { Icons } from "@/components/ui/icons";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

const fields: FormField[] = [
  {
    name: "email",
    label: "Email",
    placeholder: "example@example.com",
    type: "text",
    validation: z.string().min(2, {
      message: "Email must be at least 2 characters long",
    }),

  },
  {
    name: "password",
    label: "Password",
    placeholder: "********",
    type: "password",
    validation: z.string().min(2, {
      message: "Password must be at least 2 characters long",
    }),
  },
];

const formSchema = z.object(
  fields.reduce((acc, field) => {
    acc[field.name] = field.validation;
    return acc;
  }, {} as Record<string, z.ZodType>)
);

export default function Login() {
  const [isLoading, setIsloading] = useState<boolean>(false);

  const router = useRouter();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "test@test.com",
      password: "admin",
    },
  });

  const onSubmit = form.handleSubmit(
    async (values: z.infer<typeof formSchema>) => {
      try {
        setIsloading(true);
        const response = await signIn("credentials", {
          email: values.email,
          password: values.password,
          redirect: false,
        });

        console.log("response", response);

        if (response?.error) {
          if (response.error === "CredentialsSignin") {
            toast.error("Invalid username or password");
          }
        } else {
          router.push("/web");
        }
      } catch (error) {
        console.log(error);
      } finally {
        setIsloading(false);
      }
    }
  );

  return (
    <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="w-full max-w-sm">
        <Form {...form}>
          <form className="flex flex-col gap-6 px-4">
            <div className="flex flex-col items-center gap-2">
              <TelescopeIcon className="w-8 h-8" />
              <h1 className="text-3xl font-bold">Welcome to Hackiathon</h1>
              <span className="text-xl text-muted-foreground">
                A simple way to develop your ideas
              </span>
              <div className="text-center text-sm text-muted-foreground">
                Don&apos;t have an account?{" "}
                <Link
                  href="/register"
                  className="underline underline-offset-4 text-primary"
                >
                  Sign up
                </Link>
              </div>
            </div>
            <div className="flex flex-col gap-2">
              {fields.map((field) => (
                <CustomField key={field.name} form={form} fieldInfo={field} />
              ))}
            </div>
            <Button type="button" className="cursor-pointer" onClick={onSubmit}>
              Login{" "}
              {isLoading && <Icons.spinner className="animate-spin size-5" />}
            </Button>
            <div className="flex justify-center gap-4">
              <Link
                href="https://github.com/ElPitagoras14"
                target="_blank"
                className="flex items-center gap-2"
              >
                <SiGithub />
                <span>Github</span>
              </Link>
              <Link
                href="https://buymeacoffee.com/jhonyg"
                target="_blank"
                className="flex items-center gap-2"
              >
                <SiBuymeacoffee />
                <span>Support it</span>
              </Link>
            </div>
          </form>
        </Form>
      </div>
    </div>
  );
}
