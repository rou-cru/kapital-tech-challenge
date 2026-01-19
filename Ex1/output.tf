output "bucketArn" {
  description = "ARN del bucket"
  value       = aws_s3_bucket.s3.arn
}

output "bucketName" {
  description = "Nombre del bucket"
  value       = aws_s3_bucket.s3.bucket
}

output "clusterEndpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "clusterSecurityGroupId" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "region" {
  description = "AWS region"
  value       = var.region
}

output "clusterName" {
  description = "Kubernetes Cluster Name"
  value       = module.eks.cluster_name
}
