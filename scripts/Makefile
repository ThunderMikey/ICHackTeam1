import_keys:
	aws ec2 import-key-pair --key-name "tmikey@xps" \
		--public-key-material file://~/.ssh/id_rsa.pub

create_security_group:
	aws ec2 create-security-group --group-name ichack-sg \
		--description "Security group for development environment"

modify_firewall:
	aws ec2 authorize-security-group-ingress \
		--group-name ichack-sg --protocol tcp --port 22 \
		--cidr 0.0.0.0/0

launch_instance:
	aws ec2 run-instances --image-id ami-0b0a60c0a2bd40612 \
		--security-group-ids sg-00af6f20b7fd6bd92 \
		--count 1 \
		--instance-type t2.micro \
		--key-name tmikey@xps \
		--query "Instances[0].InstanceId"
