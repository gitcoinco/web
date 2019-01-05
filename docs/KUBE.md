# kube setup

## install

brew update
### install kubectl and AWS
brew install kubernetes-cli
brew install aws-cli
brew install aws
brew link kubernetes-cli

### install aws-iam-authenticator
curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.11.5/2018-12-06/bin/darwin/amd64/aws-iam-authenticator 
# mv to your path

aws configure
### enter your path

### completion
### https://kubernetes.io/docs/tasks/tools/install-kubectl
awscli us-west-2 kubectl completion bash > $(brew --prefix)/etc/bash_completion.d/kubectl

### now you can use kubecontrol. our cluster uses 1.10

# using it 

kubectl config get-contexts
kubectl config use-context


## using the proxy
kubectl proxy

## you can now go to 
http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/#!/login


# exec into a pod

kubectl exec <pod-name> <command> --namespace=<namespace>
kubectl exec prometheus-op-kube-state-metrics-85b7ffcb89-s96z7 /bin/bash --namespace=monitoring

# other tools

https://gam.gitcoin.co/login
http://grafana.com/dashboards
prometheus -- out of the box alerts /logs
did you know that you can run your standard docker commands in kubectl? neato
    kubectl get pods --namespace=gc-production
    kubectl get services --namespace=monitoring
    kbuectl get ingress web --namespace notifications
http://github.com/helm 
    predefined deployments you can use.
ingress docs => https://kubernetes.io/docs/concepts/services-networking/ingress/


# questions 


how do i spin up grants.gitcoin.co
TODO: access to https://gam.gitcoin.co/login
what is ingress?




