variable "s3Name" {
  type    = string
  default = "training-datasets"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "clusterVersion" {
  type    = string
  default = "1.33"
}

variable "clusterName" {
  type    = string
  default = "ML-EKS"
}

variable "nodeInstanceTypes" {
  type    = list(string)
  default = ["m5.xlarge"]
}

variable "vpcId" {
  type = string
}

variable "privateSubnetIds" {
  type = list(string)
}

variable "publicSubnetIds" {
  type = list(string)
}

variable "tags" {
  type    = map(string)
  default = {}
}
