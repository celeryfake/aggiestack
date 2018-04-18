import getopt, sys
from prettytable import PrettyTable
from collections import OrderedDict

def eprint(arg):
	print >> sys.stderr, arg

def usage_config():
	print "config command usage"
	print "command arguments: aggiestack config "
	print "positional arguments:"
	print "--hardware\t\tRead the hardware configuration file"
	print "--images\t\tRead the images configuration file"
	print "--flavors\t\tRead the flavor instances configuration file"

def usage_show():
	print "show command usage"
	print "command arguments: "
	print "aggiestack show hardware\tList the hardware information"
	print "aggiestack show images\t\tList the images information"
	print "aggiestack show flavors\t\tList the flavor information"
	print "aggiestack show all\t\tList all the information"

def usage():
	usage_config()
	usage_show()

def show_all():
	HW.show()
	IMG.show()
	FLV.show()

class Rack:
	def __init__(self, name, size):
		self.name = name
		self.capacity = size
		self.image_list = []
	def find_image(self, image):
		return image in self.image_list
	def update_image(self, image):
		self.image_list.remove(image)
		self.image_list.append(image)
	def insert_image(self, image):
		self.image_list.append(image)
		self.capacity -= image["size"];
	def remove_image(self):
		pop_img = self.image_list.pop(0)
		self.capacity += pop_img["size"]
		return pop_img["size"]
	def list(self):
		attr_str = "Rack Name: "+self.name+", Availale space: "+str(self.capacity)
		attr = [attr_str]
		t = PrettyTable(attr)
		for i in self.image_list:
			t.add_row([i["image-name"]])
		print t

class Hardware:
	def __init__(self):
		self.hw_list = OrderedDict()
		self.rk_list = OrderedDict()
		self.rk_attr_list = ["name", "capacity", "image-cache"]
		self.hw_attr_list = ["name", "rack", "ip", "mem", "num-disk", "num-vcpus"]
		self.sick_rack_list = []
	def insert_rack(self, rk_inst):
		rk_dict = OrderedDict()
		rk_dict["name"] = rk_inst[0]
		rk_dict["capacity"] = int(rk_inst[1])
		rk_dict["image-cache"] = Rack(rk_dict["name"], rk_dict["capacity"])
		self.rk_list[rk_dict["name"]] = rk_dict
	def insert_sick_rack(self, rack_name):
		if rack_name in self.sick_rack_list:
			self.sick_rack_list.append(rack_name)
	def insert_machine(self, hw_inst):
		hw_dict = OrderedDict()
		hw_dict["name"] = hw_inst[0]
		hw_dict["rack"] = hw_inst[1]
		hw_dict["ip"] = hw_inst[2]
		hw_dict["mem"] = int(hw_inst[3])
		hw_dict["num-disk"] = int(hw_inst[4])
		hw_dict["num-vcpus"] = int(hw_inst[5])
		self.hw_list[hw_dict["name"]] = hw_dict
	def remove_machine(self, machine_name):
		return self.hw_list.pop(machine_name)
	def get_machine(self, machine_name):
		return self.hw_list[machine_name]
	def get_machine_list(self, rack_name):
		machine_list = []
		for k, v in self.hw_list.items():
			if v["rack"] == rack_name:
				machine_list.append(k)
		return machine_list
	def find_rack_with_image(self, image_name):
		# simple first fit algorithm for finding image in image cache
		for k, v in self.rk_list.items():
			if v["image-cache"].find_image(image_name) == True:
				return k
		return None
	def find_rack_with_maxspace(self, exclude_list):
		max_space = -1
		rack = None
		for k, v in self.rk_list.items():
			if v["image-cache"].capacity > max_space and k not in exclude_list:
				max_space = v["image-cache"].capacity
				rack = k
		return rack, max_space
	# alloc resources flavor requires from a machine
	def alloc(self, machine, flavor):
		alloc_list = ["mem", "num-disk", "num-vcpus"]
		for i in alloc_list:
			self.hw_list[machine][i] -= flavor[i]
	# release resources flavor requires from a machine
	def release(self, machine, flavor):
		release_list = ["mem", "num-disk", "num-vcpus"]
		for i in release_list:
			self.hw_list[machine][i] += flavor[i]
	def show(self):
		rk_attr_list = ["rack-name", "storage-capacity(MB)"]
		rk_show_attr = ["name", "capacity"]
		t_rk = PrettyTable(rk_attr_list)
		for k, v in self.rk_list.items():
			row = [v[x] for x in rk_show_attr]
			t_rk.add_row(row)
		print t_rk
		t_hw = PrettyTable(self.hw_attr_list)
		for k, v in self.hw_list.items():
			t_hw.add_row(v.values())
		print t_hw
	def show_imagecaches(self, rack_name):
		self.rk_list[rack_name]["image-cache"].list()

class Images:
	def __init__(self):
		self.img_list = OrderedDict()
		self.img_attr_list = ["image-name", "size", "path"]
	def insert(self,img_inst):
		img_dict = OrderedDict()
		img_dict["image-name"] = img_inst[0]
		img_dict["size"] = int(img_inst[1])
		img_dict["path"] = img_inst[2]
		self.img_list[img_dict["image-name"]] = img_dict
	def get_image(self, image_name):
		return self.img_list[image_name]
	def show(self):
		show_attr_list = ["image-name", "size(MB)", "path"]
		t = PrettyTable(show_attr_list)
		for k, v in self.img_list.items():
			t.add_row(v.values())
		print t

class Flavors:
	def __init__(self):
		self.flv_list = OrderedDict()
		self.flv_attr_list = ["type", "mem", "num-disk", "num-vcpus"]
	def insert(self,flv_inst):
		flv_dict = OrderedDict() 
		flv_dict["type"] = flv_inst[0]
		flv_dict["mem"] = int(flv_inst[1])
		flv_dict["num-disk"] = int(flv_inst[2])
		flv_dict["num-vcpus"] = int(flv_inst[3])
		self.flv_list[flv_dict["type"]] = flv_dict
	def get_flavor(self, flavor_name):
		return self.flv_list[flavor_name]
	def show(self):
		t = PrettyTable(self.flv_attr_list)
		for k, v in self.flv_list.items():
			t.add_row(v.values())
		print t

class Instance:
	def __init__(self):
		self.inst_list = OrderedDict()
		self.inst_attr_list = ["name", "rack", "machine", "image", "flavor"]
	def add(self, inst):
		inst_dict = OrderedDict() 
		inst_dict["name"] = inst[0]
		inst_dict["rack"] = inst[1]
		inst_dict["machine"] = inst[2]
		inst_dict["image"] = inst[3]
		inst_dict["flavor"] = inst[4]
		self.inst_list[inst_dict["name"]] = inst_dict
	def get_instance(self, inst_name):
		return self.inst_list.get(inst_name)
	def get_instances_from_rack(self, rack_name):
		instances_list = []
		for k, v in self.inst_list.items():
			if v["rack"] == rack_name:
				instances_list.append(k)
		return instances_list
	def change_name(self, old_name, new_name):
		self.inst_list[old_name]["name"] = new_name
		self.inst_list[new_name] = self.inst_list.pop(old_name)
	def remove(self, inst_name):
		self.inst_list.pop(inst_name, None)
	def list(self):
		list_attr = list(self.inst_attr_list)
		list_attr.remove("machine")
		t = PrettyTable(list_attr)
		for k, v in self.inst_list.items():
			row = [v[x] for x in list_attr]
			t.add_row(row)
		print t
	def show_instances(self):
		list_attr = ["name", "rack", "machine"]
		print_list_attr = ["instance name", "rack", "physical server"]
		t = PrettyTable(print_list_attr)
		for k, v in self.inst_list.items():
			row = [v[x] for x in list_attr]
			t.add_row(row)
		print t

def do_config(option,arg):
	try:
		f = open(arg, 'r')
	except:
		eprint("No such file: "+arg)
		exit(0)
	if option == "--hardware":
		# read the rack information
		num_of_line = f.readline()
		for i in xrange(int(num_of_line)):
			rk_inst = f.readline()
			rk_inst = rk_inst.split()
			HW.insert_rack(rk_inst)
			HW_free.insert_rack(rk_inst)
		# read the machine information
		num_of_line = f.readline()
		for i in xrange(int(num_of_line)):
			hw_inst = f.readline()
			hw_inst = hw_inst.split()
			HW.insert_machine(hw_inst)
			HW_free.insert_machine(hw_inst)
	elif option == "--images":
		num_of_line = f.readline()
		for i in xrange(int(num_of_line)):
			img_inst = f.readline()
			img_inst = img_inst.split()
			IMG.insert(img_inst)
	elif option == "--flavors":
		num_of_line = f.readline()
		for i in xrange(int(num_of_line)):
			flv_inst = f.readline()
			flv_inst = flv_inst.split()
			FLV.insert(flv_inst)

def check_can_host(machine, flavor):
	m_inst = HW_free.get_machine(machine)
	f_inst = FLV.get_flavor(flavor)
	check_list = ["mem", "num-disk", "num-vcpus"]
	can_host = True
	for i in check_list:
		if int(f_inst[i]) > int(m_inst[i]):
			can_host = False
			break;
	return can_host

def server_create_in_rack(name, rack, image_name, flavor_type):
	flavor = FLV.get_flavor(flavor_type)
	machine_list = HW_free.get_machine_list(rack)
	# simple first fit algorithm for allocation
	for i in machine_list:
		if check_can_host(i, flavor_type) == True:
			HW_free.alloc(i, flavor)
			inst = [name, i, image_name, flavor_type]
			INST.add(inst)
			return True
	return False

def server_create(name, image_name, flavor_type):
	# copy the sick racks to unavail_rack_list
	unavail_rack_list = HW_free.sick_rack_list[:]
	image = IMG.get_image(image_name)
	create_success = False
	while len(unavail_rack_list) != len(HW_free.rk_list.keys()):
		# first check rack server cache, see if contains image
		rack = HW_free.find_rack_with_image(image_name)
		# if found rack contain image allocate on that rack
		if rack is not None and rack not in unavail_rack_list:
			HW_free.rk_list[rack]["image-cache"].update_image(image)
			create_success = server_create_in_rack(name, rack, image_name, flavor_type)
			# add to unavail_rack_list if no resources
			if create_success == False:
				unavail_rack_list.append(rack)
			else:
				break
		# if not found image cache
		else:
			# first found rack with max image cache space
			rack, avail_space = HW_free.find_rack_with_maxspace(unavail_rack_list)
			# evict image until there is enough space for the image
			while avail_space < image["size"]:
				avail_space += HW_free.rk_list[rack]["image-cache"].remove_image()
			HW_free.rk_list[rack]["image-cache"].insert_image(image)
			create_success = server_create_in_rack(name, rack, image_name, flavor_type)
			# add to unavail_rack_list if no resources
			if create_success == False:
				unavail_rack_list.append(rack)
			else:
				break
	return create_success


def server_delete(name):
	inst = INST.get_instance(name)
	if inst is None:
		return False
	machine = inst["machine"]
	flavor = FLV.get_flavor(inst["flavor"])
	HW_free.release(machine, flavor)
	INST.remove(name)
	return True

def server_update_name(old_name, new_name):
	INST.change_name(old_name, new_name)

def server_migrate(name):
	inst = INST.get_instance(name)
	image_name = inst["image"]
	flavor_type = inst["flavor"]
	migrate_success = server_create(name+"_temp", image_name, flavor_type)
	if migrate_success == True:
		server_delete(name)
		server_update_name(name+"_temp", name)
	return migrate_success

HW=Hardware()
HW_free=Hardware()
IMG=Images()
FLV=Flavors()
INST=Instance()

def main():
	while True:
		argv = raw_input('> ')
		argv = argv.split()
		try:
			program_name = argv[0]
		except:
			usage()

		# valid test
		if program_name == "q" or program_name == "quit":
			exit(0)
		elif program_name != "aggiestack":
			usage()
			continue
		try:
			issuer = argv[1]
			if issuer != "admin" and issuer != "server":
				issuer = None
				cmd = argv[1]
			else:
				cmd = argv[2]
		except:
			usage()
			continue

		if issuer is None:
			if cmd == "config":
				try:
					opts, args = getopt.getopt(argv[2:], "h", ["hardware=", "images=", "flavors="])
				except getopt.GetoptError as err:
					eprint(str(err))  # will print something like "option -a not recognized"
					usage_config()
				if len(opts) == 0:
					usage_config()
				for o, a in opts:
					if o == "--hardware" or o == "--images" or o == "--flavors":
						do_config(o,a)
					else:
						usage_config()

			elif cmd == "show":
				try:
					cmd = argv[2]
					if cmd == "hardware":
						HW.show()
					elif cmd == "images":
						IMG.show()
					elif cmd == "flavors":
						FLV.show()
					elif cmd == "all":
						show_all()
					else:
						usage_show()
				except:
					usage_show()
		elif issuer == "admin":
			if cmd == "show":
				try:
					suffix = argv[3]
					if suffix == "hardware":
						HW_free.show()
					elif suffix == "instances":
						INST.show_instances()
					elif suffix == "imagecaches":
						try:
							rack = argv[4]
							HW_free.show_imagecaches(rack)
						except:
							usage_show()
					else:
						usage_show()
				except:
					usage_show()	
			elif cmd == "can_host":
				try:
					machine_name = argv[3]
					flavor_type = argv[4]
					print check_can_host(machine_name, flavor_type)
				except:
					usage_show()
			elif cmd == "add":
				try:
					opts, args = getopt.getopt(argv[3:], "h", ["mem=", "disk=", "vcpus=", "ip=", "rack="])
				except getopt.GetoptError as err:
					eprint(str(err))  # will print something like "option -a not recognized
				if len(opts) != 5 or args is None:
					usage_show()
				for o, a in opts:
					if o == "--mem":
						mem = a
					if o == "--disk":
						disk = a
					if o == "--vcpus":
						vcpus = a
					if o == "--ip":
						ip = a
					if o == "--rack":
						rack = a
				hw_inst = [args[0], rack, ip, mem, disk, vcpus]
				HW.insert_machine(hw_inst)
				HW_free.insert_machine(hw_inst)			
			elif cmd == "remove":
				try:
					machine_name = argv[3]
					ret = HW_free.remove_machine(machine_name)
					if ret == machine_name:
						# also remove from HW
						HW.remove_machine(machine_name)
					else:
						err = machine_name + " not exist in hardware list!"
						eprint(err)
				except:
					usage_show()
			elif cmd == "evacuate":
				try:
					rack_name = argv[3]
					HW.insert_sick_rack(rack_name)
					HW_free.insert_sick_rack(rack_name)
					instances_list = INST.get_instances_from_rack(rack_name)
					migrate_list = []
					for i in instances_list:
						if server_migrate(i) == True:
							migrate_list.append(i)
							instances_list.remove(i)
						else:
							eprint("Evacuate "+rack_name+"terminated due to resources limitation, please remove some instances")
							eprint("Successful migrated instances: "+str(migrate_list))
							eprint("Left instances: "+str(instances_list))
							break
				except:
					usage_show()
		elif issuer == "server":
			if cmd == "create":
				try:
					opts, args = getopt.getopt(argv[3:], "h", ["image=", "flavor="])
				except getopt.GetoptError as err:
					eprint(str(err))  # will print something like "option -a not recognized
				if len(opts) != 2 or args is None:
					usage_show()
				for o, a in opts:
					if o == "--image":
						image_name = a
					if o == "--flavor":
						flavor_type = a
				inst_name = args[0]
				create_success = server_create(inst_name, image_name, flavor_type)
				if create_success == False:
					eprint("No more available resources")
			elif cmd == "delete":
				inst_name = argv[3]
				if server_delete(inst_name) == False:
					err = inst_name + " instance not exist!"
					eprint(err)
			elif cmd == "list":
				INST.list()


if __name__ == "__main__":
    main()
