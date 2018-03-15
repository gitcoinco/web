DISTID=$1
aws cloudfront create-invalidation --distribution-id $DISTID --invalidation-batch="Paths={Quantity=1,Items=["/*"]},CallerReference=$(date)"
