#------------------------------------------------------------------------------
# The Release workflow's access to the docs site.
#
# After a release reaches PyPI, the workflow's publish-docs job uploads the
# site and invalidates CloudFront. It signs in with GitHub's OIDC token, so no
# AWS key is stored in GitHub, and only a job in this repository's "docs"
# environment can assume the role. That environment is limited to main in the
# repository's settings, as the "pypi" environment is.
#------------------------------------------------------------------------------

# GitHub's OIDC provider is one per AWS account, and cache-results'
# terraform/docs already creates it. Creating a second one would fail, so this
# stack only reads it: apply cache-results' stack first.
data "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "docs_publisher_trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github_actions.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repository}:environment:${var.github_environment}"]
    }
  }
}

resource "aws_iam_role" "docs_publisher" {
  name               = "smarter-python-docs-publisher"
  description        = "The smarter-python Release workflow, publishing ${var.domain_name}"
  assume_role_policy = data.aws_iam_policy_document.docs_publisher_trust.json
}

# Exactly what make sphinx-publish does: sync the bucket, and invalidate the distribution.
data "aws_iam_policy_document" "docs_publisher" {
  statement {
    sid       = "ListTheBucket"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.docs.arn]
  }

  statement {
    sid       = "SyncTheSite"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.docs.arn}/*"]
  }

  statement {
    sid       = "InvalidateTheDistribution"
    actions   = ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"]
    resources = [aws_cloudfront_distribution.docs.arn]
  }
}

resource "aws_iam_role_policy" "docs_publisher" {
  name   = "publish-docs"
  role   = aws_iam_role.docs_publisher.id
  policy = data.aws_iam_policy_document.docs_publisher.json
}
