Vagrant.configure("2") do |config|

  config.vm.define "db" do |db|
    db.vm.box = "ubuntu/bionic64"
    db.vm.network "private_network", ip: "10.0.0.11"
    db.vm.network "forwarded_port", guest: 5432, host: 5432
    db.vm.hostname = "db"
    db.ssh.insert_key = false
    db.vm.provision "ansible" do |ansible|
      ansible.verbose = "v"
      ansible.playbook = "ansible/test-connection.yml"
    end
  end
  
  config.vm.define "web" do |web|
    web.vm.box = "ubuntu/bionic64"
    web.vm.network "private_network", ip: "10.0.0.10"
    web.vm.network "forwarded_port", guest: 8000, host: 8000
    web.vm.network "forwarded_port", guest: 3030, host: 3030
    web.vm.network "forwarded_port", guest: 8001, host: 8001
    web.vm.network "forwarded_port", guest: 35729, host: 35729
    web.vm.hostname = "web"
    web.ssh.insert_key = false
    web.vm.provision "ansible" do |ansible|
      ansible.verbose = "v"
      ansible.playbook = "ansible/test-connection.yml"
    end
  end
end
