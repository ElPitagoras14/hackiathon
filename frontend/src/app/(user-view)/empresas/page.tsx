"use client"

import { useState } from "react";
import { Search, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useCompany } from "@/providers/company-provider";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";

export default function CompanyPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const { companies, addCompany ,loading} = useCompany();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newCompany, setNewCompany] = useState({
    ruc: "",
    nombre: "",
    instagramLink: "",
    industry:"",
  });


  const filteredCompanies = companies.filter(
    (company) =>
      company.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddCompany = () => {
    if (newCompany.ruc && newCompany.nombre && newCompany.instagramLink) {
      console.log("Adding new company:", newCompany);
      console.log("Company data:", {
        name: newCompany.nombre,
        ruc: newCompany.ruc,
        igUrl: newCompany.instagramLink,
        industry: newCompany.industry || "Empresa",
      });
      addCompany({
        name: newCompany.nombre,
        ruc: newCompany.ruc,
        igUrl: newCompany.instagramLink,
        industry: newCompany.industry || "Empresa",
      });
      setNewCompany({ ruc: "", nombre: "", instagramLink: "", industry: "" });
      setIsDialogOpen(false);
    }
  };
  


  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="w-full px-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Seleccionar compañía
              </h1>
              <p className="text-gray-600">
                Selecciona una compañía de la lista de abajo o crea una nueva
                compañía
              </p>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-gray-900 hover:bg-gray-800 text-white">
                  <Plus className="h-4 w-4 mr-2" />
                  Añadir nueva compañía
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-white border-gray-200">
                <DialogHeader>
                  <DialogTitle className="text-gray-900">
                    Agregar Nueva Compañía
                  </DialogTitle>
                  <DialogDescription className="text-gray-600">
                    Ingresa los datos básicos de la nueva compañía
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="ruc" className="text-gray-900">
                      RUC
                    </Label>
                    <Input
                      id="ruc"
                      placeholder="20123456789"
                      value={newCompany.ruc}
                      onChange={(e) =>
                        setNewCompany({ ...newCompany, ruc: e.target.value })
                      }
                      className="border-gray-300 text-gray-900"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="nombre" className="text-gray-900">
                      Nombre de la Compañía
                    </Label>
                    <Input
                      id="nombre"
                      placeholder="Nombre de la compañía"
                      value={newCompany.nombre}
                      onChange={(e) =>
                        setNewCompany({ ...newCompany, nombre: e.target.value })
                      }
                      className="border-gray-300 text-gray-900"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="instagram" className="text-gray-900">
                      Link de Instagram
                    </Label>
                    <Input
                      id="instagram"
                      placeholder="https://instagram.com/empresa"
                      value={newCompany.instagramLink}
                      onChange={(e) =>
                        setNewCompany({
                          ...newCompany,
                          instagramLink: e.target.value,
                        })
                      }
                      className="border-gray-300 text-gray-900"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="industry" className="text-gray-900">
                      Industria
                    </Label>
                    <Select
                      value={newCompany.industry || undefined}
                      onValueChange={(val) =>
                        setNewCompany({ ...newCompany, industry: val })
                      }
                    >
                      <SelectTrigger
                        id="industry"
                        className="w-full border-gray-300 text-gray-900"
                      >
                        <SelectValue placeholder="Selecciona la industria" />
                      </SelectTrigger>
                      <SelectContent className="w-[--radix-select-trigger-width]">
                        <SelectItem value="Finance">Finanzas</SelectItem>
                        <SelectItem value="Technology">Tecnología</SelectItem>
                        <SelectItem value="Construction">
                          Construcción
                        </SelectItem>
                        <SelectItem value="Manufacturing">
                          Manufactura
                        </SelectItem>
                        <SelectItem value="Retail">Comercio</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setIsDialogOpen(false)}
                    className="border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-gray-900 
             dark:border-gray-600 dark:text-black dark:hover:bg-gray-200 "
                  >
                    Cancelar
                  </Button>
                  <Button
                    onClick={handleAddCompany}
                    className="bg-gray-900 hover:bg-gray-800 text-white"
                    disabled={
                      !newCompany.ruc ||
                      !newCompany.nombre ||
                      !newCompany.instagramLink
                    }
                  >
                    Agregar Compañía
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              placeholder="Busca tu compañía"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-12 py-3 text-lg border-2 border-gray-300 rounded-xl focus:border-gray-900 focus:ring-0 text-gray-900"
            />
          </div>
        </div>

        {/* Companies List */}
        <div className="bg-white rounded-2xl border-2 border-gray-200 p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Compañías existentes
          </h2>
          {loading ? (
            <div className="text-center py-8">
              <p className="text-gray-500">Cargando compañías...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredCompanies.map((company) => (
                <div
                  key={company.id}
                  className="flex items-center space-x-4 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex flex-col">
                      <span className="text-lg font-medium text-gray-900">
                        {company.name}
                      </span>
                      <span className="text-sm text-gray-500">
                        {company.industry}
                      </span>
                      <span className="text-xs text-gray-400 mt-1">
                        RUC: {company.ruc}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <a
                      href={company.igUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      Ver Instagram
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}

          {filteredCompanies.length === 0 && !loading && (
            <div className="text-center py-8">
              <p className="text-gray-500">No se encontraron compañías</p>

              <p className="text-sm text-gray-400 mt-1">
                {searchTerm
                  ? "Intenta con otros términos de búsqueda"
                  : "Agrega tu primera compañía"}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
