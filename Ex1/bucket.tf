// Garantizar un nombre unico para el bucket
resource "random_string" "s3Suffix" {
  length  = 8
  upper   = false
  special = false
}

// El bucket
resource "aws_s3_bucket" "s3" {
  #checkov:skip=CKV2_AWS_61
  #checkov:skip=CKV_AWS_18
  #checkov:skip=CKV2_AWS_62
  #checkov:skip=CKV_AWS_144
  bucket = "${var.s3Name}-${random_string.s3Suffix.result}"

  tags = var.tags
}

// Rollback de datos
resource "aws_s3_bucket_versioning" "versioned" {
  bucket = aws_s3_bucket.s3.id
  versioning_configuration {
    status = "Enabled"
  }
}

// Acceso solo privado
resource "aws_s3_bucket_public_access_block" "private" {
  bucket = aws_s3_bucket.s3.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

// Cifrado en reposo
resource "aws_s3_bucket_server_side_encryption_configuration" "kms" {
  bucket = aws_s3_bucket.s3.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}
