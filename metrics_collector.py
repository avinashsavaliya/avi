# Authors: savaliyaa

import os

def run_local_cmd(command):
    try:
        proc = os.popen(command).read().strip()
        print(proc)
        return proc
    except Exception as e:
        print(e)


def get_sv_node_id():
    stdout = run_local_cmd("hostname")
    return stdout


def get_active_pods_name(ns):
    cmd = "kubectl get pods -n {ns} -o wide | grep -i {sv_node}".format(ns=ns,sv_node=current_sv_node)+" | awk '{print $1}'"
    #print("Active Pod command for namespace {} : {}".format(ns, cmd))
    pods = run_local_cmd(cmd).split("\n")
    print("Active PODS are : {}".format(pods))
    return pods


def retrieve_container_id(pod_name, ns):
    cmd = "kubectl get pod {} -n {}".format(pod_name,ns) + " -o jsonpath='{.status.containerStatuses[1].name}'"
    cname = run_local_cmd(cmd)
    if str(cname) == 'manager':
        id_cmd = "kubectl get pod {} -n {}".format(pod_name,ns) + " -o jsonpath='{.status.containerStatuses[1].containerID}'"
        cid = run_local_cmd(id_cmd).split("//")[-1]
        return cid, cname

    else:
        cmd = "kubectl get pod {} -n {}".format(pod_name, ns) + " -o jsonpath='{.status.containerStatuses[0].name}'"
        cname = run_local_cmd(cmd)
        if str(cname) == 'manager':
            id_cmd = "kubectl get pod {} -n {}".format(pod_name,ns) + " -o jsonpath='{.status.containerStatuses[0].containerID}'"
            cid = run_local_cmd(id_cmd).split("//")[-1]
            return cid, cname


def collect_container_metrics(id):

    #cmd = "crictl stats {} >> {}".format(id,fname)
    cmd = "crictl stats {}".format(id)
    stdout = run_local_cmd(cmd)
    print("collector metrics : {}".format(stdout))
    return stdout


def write_to_file(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(data+"\n\n")


def main():

    ns_list = ["vmware-system-tkg","vmware-system-nsop"]
    print("Current SV Node hostname : {}".format(current_sv_node))

    for ns in ns_list:
        output = "\n==================================================   " + ns + \
                 "   ==================================================\n"

        active_pods = get_active_pods_name(ns)
        for pod in active_pods:

            output += "\n Pod : " + pod + "   \n\n"
            cid, cname = retrieve_container_id(pod, ns)
            output += "container name  : " + cname + "     container id : " + cid + "\n\n"
            #print(output)
            metrics = collect_container_metrics(cid)
            output += "\n" + metrics + "\n"

        #write_to_file(output, ns+".txt")

        with open("resource_metrics.txt", 'a+', encoding='utf-8') as f:
            f.write(output + "\n\n")


if __name__ == "__main__":

    current_sv_node = get_sv_node_id()
    main()