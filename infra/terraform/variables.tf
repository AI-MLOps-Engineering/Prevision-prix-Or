variable "scw_access_key" {
  description = "Scaleway access key"
  type        = string
}

variable "scw_secret_key" {
  description = "Scaleway secret key"
  type        = string
}

variable "scw_project_id" {
  description = "Scaleway project id"
  type        = string
}

variable "instance_type" {
  description = "Scaleway instance type"
  type        = string
  default     = "DEV1-L"
}

variable "instance_name" {
  description = "Name for the Scaleway instance"
  type        = string
  default     = "gold-forecasting"
}

variable "ssh_public_key" {
  description = "Contenu de la clé publique SSH (ex: contenu de id_ed25519.pub)"
  type        = string
}

variable "ssh_private_key_path" {
  description = "Chemin local vers la clé privée utilisée par le provisioner (ne pas committer)"
  type        = string
  default     = "~/.ssh/id_ed25519"
}

variable "ssh_user" {
  type    = string
  default = "root"
}

variable "repo_url" {
  type    = string
  default = "https://github.com/AI-MLOps-Engineering/Prevision-prix-Or.git"
}
