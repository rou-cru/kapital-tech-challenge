// El cluster
module "eks" {
  #checkov:skip=CKV_TF_1
  source  = "terraform-aws-modules/eks/aws"
  version = "20.8.5"

  cluster_name    = var.clusterName
  cluster_version = var.clusterVersion

  cluster_endpoint_public_access           = true
  enable_cluster_creator_admin_permissions = true

  tags = merge(var.tags, {
    k8sVersion = var.clusterVersion
  })

  vpc_id                   = var.vpcId
  subnet_ids               = var.privateSubnetIds
  control_plane_subnet_ids = var.publicSubnetIds

  eks_managed_node_groups = {
    default = {
      instance_types = var.nodeInstanceTypes
    }
  }
}
