#!/usr/bin/env python3.9
import os
import shlex
def process_curl():
    # TEST_CLIENT_POD #
    # TEST_SERVER_HTTP_DST_PORT #
    # FT_CLIENT_CPU_MASK #
    test_server_http_dst = os.environ['TEST_SERVER_HTTP_DST']
    test_server_http_dst_port = os.environ['TEST_SERVER_HTTP_DST_PORT']
    test_client_pod = os.environ['TEST_CLIENT_POD']
    test_server_http_dst = os.environ['TEST_SERVER_HTTP_DST']
    test_client_pod = os.environ['TEST_CLIENT_POD']
    test_server_http_dst = os.environ['TEST_SERVER_HTTP_DST']
    test_server_http_dst_port = os.environ['TEST_SERVER_HTTP_DST_PORT']
    server_path = os.environ["SERVER_PATH"]
    curl_cmd = os.environ["CURL_CMD"]
    verbose = os.environ["VERBOSE"]
    ft_namespace = os.environ["FT_NAMESPACE"]
    test_server_rsp = os.environ["TEST_SERVER_RSP"]
    kubeapi_server_string = os.environ["KUBEAPI_SERVER_STRING"]
    my_cluster = os.environ["MY_CLUSTER"] #
    test_client_node = os.environ["TEST_CLIENT_NODE"]  #
    test_server_cluster = os.environ["TEST_SERVER_CLUSTER"] #
    test_server_node = os.environ["TEST_SERVER_NODE"] #
    print("=== CURL ===")
    print(f"{my_cluster}:{test_client_node} -> {test_server_cluster}:{test_server_node}")

    if not test_client_pod:
        # From External (no 'kubectl exec')
        print(f"{curl_cmd} \"http://{test_server_http_dst}:{test_server_http_dst_port}{server_path}\"")
        curl_with_args= shlex.split(curl_cmd)
        curl_with_args.append(f"http://{test_server_http_dst}:{test_server_http_dst_port}{server_path}")
        tmp_output= subprocess.run(curl_with_args, capture_output = True, text = True)

    elif not test_server_http_dst_port:
        print(f"kubectl exec -n {ft_namespace} {test_client_pod} -- {curl_cmd} \"http://{test_server_http_dst}/\"")
        kubectl_cmd = ["kubectl", "exec", "-n", ft_namespace, test_client_pod, "--", f'{curl_cmd} "http://{test_server_http_dst}/"']
        tmp_output= subprocess.run(kubectl_cmd, capture_output = True, text = True)
    else:
        # Default command

        # If Kubebernetes API, include --cacert and -H TOKEN
        if test_server_rsp == kubeapi_server_string:
            lcl_service_account ="/var/run/secrets/kubernetes.io/serviceaccount"
            print("lcl_token=kubectl exec -n {ft_namespace} {test_client_pod} -- cat {lcl_service_account}/token"
            kubectl_cmd= ["kubectl", "exec", "-n", ft_namespace, test_client_pod, "--", f'cat {lcl_service_account}/token']

            lcl_token= subprocess.run(kubectl_cmd, capture_output = True, text = True)

            print("kubectl exec -n {ft_namespace} {test_client_pod} -- {curl_cmd} --cacert {lcl_serviceaccount}/ca.crt  -H \"Authorization: Bearer LCL_TOKEN\" -X GET \"https://{test_server_http_dst}:{test_server_http_dst_port}/api\""

            kubectl_cmd=["kubectl", "exec", "-n", ft_namespace, test_client_pod,"--", f'{curl_cmd} --cacert {lcl_serviceaccount}/ca.crt  -H "Authorization: Bearer {lcl_token}" -X GET "https://{test_server_http_dst}:{test_server_http_dst_port}/api"']

            tmp_output= subprocess.run(kubectl_cmd, capture_output = True, text = True)

        else:
            #kubectl config get-contexts
            print(f"kubectl exec -n {ft_namespace} {test_client_pod} -- curl_cmd \"http://{test_server_http_dst}:{test_server_http_dst_port}{server_path}\"")
            kubectl_cmd=["kubectl", "exec", "-n", ft_namespace, test_client_pod, "--", f'{curl_cmd} "http://{test_server_http_dst}:{test_server_http_dst_port}{server_path}"']
            tmp_output= subprocess.run(kubectl_cmd, capture_output = True, text = True)
    
    # Dump command output
    if verbose:
        print(tmp_output)

    # Print SUCCESS or FAILURE
    green=os.environ["GREEN"]
    nc = os.environ["NC"]
    red = os.environ["RED"]
    if tmp_output.count(test_server_rsp)>0: 
        print(f"\r\n{green}SUCCESS{nc}\r\n")
    else:
        print(f"\r\n{red}FAILED{nc}\r\n")

if __name__ == "__main__":
    process_curl()
