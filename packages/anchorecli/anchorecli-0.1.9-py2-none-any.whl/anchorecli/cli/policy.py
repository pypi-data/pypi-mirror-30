import sys
import json
import click

import anchorecli.clients.apiexternal
import anchorecli.cli

config = {}

@click.group(name='policy', short_help='Policy operations')
@click.pass_obj
def policy(ctx_config):
    global config
    config = ctx_config

    try:
        anchorecli.cli.utils.check_access(config)
    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'policy', {}, err)
        sys.exit(2)

@policy.command(name='add', short_help="Add a policy bundle")
@click.argument('input_policy', nargs=1, type=click.Path(exists=True), metavar='<Anchore Policy Bundle File>')
def add(input_policy):
    ecode = 0

    try:
        with open(input_policy, 'r') as FH:
            policybundle = json.loads(FH.read())

        ret = anchorecli.clients.apiexternal.add_policy(config, policybundle=policybundle, detail=True)
        ecode = anchorecli.cli.utils.get_ecode(ret)
        if ret['success']:
            print anchorecli.cli.utils.format_output(config, 'policy_add', {}, ret['payload'])
        else:
            raise Exception(json.dumps(ret['error'], indent=4))

    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'policy_add', {}, err)
        if not ecode:
            ecode = 2

    anchorecli.cli.utils.doexit(ecode)

@policy.command(name='get', short_help="Get a policy bundle")
@click.argument('policyid', nargs=1)
@click.option("--detail", is_flag=True, help="Get policy bundle as JSON")
def get(policyid, detail):
    """
    POLICYID: Policy ID to get
    """
    ecode = 0

    try:
        ret = anchorecli.clients.apiexternal.get_policy(config, policyId=policyid, detail=detail)
        ecode = anchorecli.cli.utils.get_ecode(ret)
        if ret['success']:
            print anchorecli.cli.utils.format_output(config, 'policy_get', {'detail':detail}, ret['payload'])
        else:
            raise Exception(json.dumps(ret['error'], indent=4))

    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'policy_get', {}, err)
        if not ecode:
            ecode = 2

    anchorecli.cli.utils.doexit(ecode)

@policy.command(name='list', short_help="List all policies")
def policylist():
    ecode = 0
    
    try:
        ret = anchorecli.clients.apiexternal.get_policies(config, detail=False)
        ecode = anchorecli.cli.utils.get_ecode(ret)
        if ret['success']:
            print anchorecli.cli.utils.format_output(config, 'policy_list', {'detail':False}, ret['payload'])
        else:
            raise Exception( json.dumps(ret['error'], indent=4))

    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'policy_list', {}, err)
        if not ecode:
            ecode = 2

    anchorecli.cli.utils.doexit(ecode)

@policy.command(name='activate', short_help="Activate a policyid")
@click.argument('policyid', nargs=1)
def activate(policyid):
    """
    POLICYID: Policy ID to be activated
    """
    ecode = 0

    try:
        ret = anchorecli.clients.apiexternal.get_policy(config, policyId=policyid, detail=True)
        ecode = anchorecli.cli.utils.get_ecode(ret)
        if ret['success']:
            policy_records = ret['payload']
            policy_record = {}
            if policy_records:
                policy_record = policy_records[0]
        else:
            raise Exception(json.dumps(ret['error'], indent=4))

        if not policy_record:
            raise Exception("no policy could be fetched to activate")

        policy_record['active'] = True

        ret = anchorecli.clients.apiexternal.update_policy(config, policyid, policy_record=policy_record)
        ecode = anchorecli.cli.utils.get_ecode(ret)
        if ret['success']:
            print anchorecli.cli.utils.format_output(config, 'policy_activate', {'policyId': policyid}, ret['payload'])
        else:
            raise Exception(json.dumps(ret['error'], indent=4))

    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'policy_activate', {}, err)
        if not ecode:
            ecode = 2

    anchorecli.cli.utils.doexit(ecode)

@policy.command(name='del', short_help="Delete a policy bundle")
@click.argument('policyid', nargs=1)
def delete(policyid):
    """
    POLICYID: Policy ID to delete
    """
    ecode = 0

    try:
        ret = anchorecli.clients.apiexternal.delete_policy(config, policyId=policyid)
        ecode = anchorecli.cli.utils.get_ecode(ret)
        if ret['success']:
            print anchorecli.cli.utils.format_output(config, 'policy_delete', {}, ret['payload'])
        else:
            raise Exception(json.dumps(ret['error'], indent=4))

    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'policy_delete', {}, err)
        if not ecode:
            ecode = 2

    anchorecli.cli.utils.doexit(ecode)

@policy.command(name='describe', short_help='Describes the policy gates and triggers available')
@click.option('--gate', help='Pick a specific gate to describe instead of all')
@click.option('--trigger', help='Pick a specific trigger to describe instead of all, requires the --gate option to be specified')
def describe(gate=None, trigger=None):
    ecode = 0
    try:
        ret = anchorecli.clients.apiexternal.describe_policy_spec(config)

        if ret['success']:
            render_payload = ret['payload']

            if not gate:
                print anchorecli.cli.utils.format_output(config, 'describe_policy', {}, render_payload)
            else:
                if trigger:
                    print anchorecli.cli.utils.format_output(config, 'describe_policy_gate_trigger_params', {'gate': gate, 'trigger': trigger}, render_payload)
                else:
                    print anchorecli.cli.utils.format_output(config, 'describe_policy_gate', {'gate': gate}, render_payload)
        else:
            raise Exception(json.dumps(ret['error'], indent=4))

    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'describe_policy', {}, err)
        if not ecode:
            ecode = 2

    anchorecli.cli.utils.doexit(ecode)
