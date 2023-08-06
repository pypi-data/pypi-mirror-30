"""gRPC LogicModule Client code - LogicModule methods."""

from datetime import datetime
import itertools
import logging
import sys
import traceback

import grpc
from grpc._cython import cygrpc

from dataclay.commonruntime.Settings import settings
from dataclay.communication.grpc.paraver.ParaverClientInterceptor import ParaverClientInterceptor
import dataclay.communication.grpc.messages.common.common_messages_pb2 as CommonMessages
from dataclay.communication.grpc import Utils
from dataclay.communication.grpc.generated.logicmodule import logicmodule_pb2_grpc
from dataclay.communication.grpc.messages.common import common_messages_pb2
from dataclay.communication.grpc.messages.logicmodule import logicmodule_messages_pb2
from dataclay.exceptions.exceptions import DataclayException
from dataclay.paraver import trace_all_public_methods
from dataclay.util.YamlParser import dataclay_yaml_dump, dataclay_yaml_load

__author__ = 'Enrico La Sala <enrico.lasala@bsc.es>'
__copyright__ = '2017 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger('dataclay.api')

async_req_send = itertools.count()
async_req_rec = itertools.count()

TIME_OUT = 15  # TODO: use configuration


@trace_all_public_methods
class LMClient(object):
    channel = None
    lm_stub = None

    backup_host = None
    backup_port = None
    
    def __init__(self, hostname, port):
        self.create_stubs(hostname, port)

    def create_stubs(self, hostname, port):
        """Create the stub and the channel at the address passed by the server."""
        address = str(hostname) + ":" + str(port)
        options = [(cygrpc.ChannelArgKey.max_send_message_length, 1000 * 1024 * 1024),
                   (cygrpc.ChannelArgKey.max_receive_message_length, 1000 * 1024 * 1024)]

        self.channel = grpc.insecure_channel(address, options)
        if settings.paraver_tracing_enabled:
            self.channel = grpc.intercept_channel(
                self.channel,
                # FIXME discover what (semantically) is originHostName and fix pywhatsthis
                ParaverClientInterceptor("pywhatsthis", hostname, port)
            )

        self.lm_stub = logicmodule_pb2_grpc.LogicModuleStub(self.channel)
        
        """
        FIXME: race condition what if we use backup and still is not new leader?
        OPTIONS: it is a must that all LM has backup -> then wait till new backup is configured by admin
        it is not a must -> dynamically adding and removing Backups? make sense?
        Test connection and get backup information if present
        """
        try:
            backup_info = self.get_backup_info()
            self.backup_host = backup_info[0]
            self.backup_port = backup_info[1]
        except Exception as e:
            traceback.print_exc()
            logger.debug("Exception while getting backup info", str(e));

    def change_to_backup(self, newhostname, newport):
        """
        @brief Change current connection 
        """
        logger.debug("Changing to backup LM");
        # self.close()
        self.create_stubs(newhostname, newport)

    def close(self):
        """Closing channel by deleting channel and stub"""
        del self.channel
        del self.lm_stub
        self.channel = None
        self.lm_stub = None
        
    def _call_logicmodule(self, request, lm_function):
        response = None
        try:
            import inspect
            logger.debug("Calling LM %s" % str(inspect.getsource(lm_function)))
            response = lm_function(request)
            logger.debug("Call to LM done");
        except Exception as e:
            logger.debug("Catch exception %s" % str(e))
            if self.backup_host is not None:
                try: 
                    self.change_to_backup(self.backup_host, self.backup_port)
                    response = lm_function(request)
                except Exception as ee: 
                    logger.debug("Exception calling LM")
                    raise ee
            else:
                logger.debug("Exception calling LM")
                raise e
        return response

    def lm_autoregister_ds(self, ds_name, ds_hostname, ds_tcp_port, ds_lang):

        request = logicmodule_messages_pb2.AutoRegisterDSRequest(
            dsName=ds_name,
            dsHostname=ds_hostname,
            dsPort=ds_tcp_port,
            lang=ds_lang
        )
        lm_function = lambda request: self.lm_stub.autoregisterDataService(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            logger.debug("Exception in response") 
            raise DataclayException(response.excInfo.exceptionMessage)

        st_loc_id = Utils.get_id(response.storageLocationID)
        ex_env_id = Utils.get_id(response.executionEnvironmentID)

        result = (st_loc_id, ex_env_id)

        return result

    def perform_set_of_new_accounts(self, admin_id, admin_credential, yaml_file):

        request = logicmodule_messages_pb2.PerformSetAccountsRequest(
            accountID=Utils.get_msg_options['account'](admin_id),
            credential=Utils.get_credential(admin_credential),
            yaml=yaml_file
        )
        lm_function = lambda request: self.lm_stub.performSetOfNewAccounts(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = bytes(response.resultYaml)
        return result

    def perform_set_of_operations(self, performer_id, performer_credential, yaml_file):

        request = logicmodule_messages_pb2.PerformSetOperationsRequest(
            accountID=Utils.get_msg_options['account'](performer_id),
            credential=Utils.get_credential(performer_credential),
            yaml=yaml_file
        )
        lm_function = lambda request: self.lm_stub.performSetOfOperations(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = bytes(response.resultYaml)

        return result

    # Methods for Account Manager

    def new_account(self, admin_account_id, admin_credential, account):

        acc_yaml = dataclay_yaml_dump(account)

        request = logicmodule_messages_pb2.NewAccountRequest(
            adminID=Utils.get_msg_options['account'](admin_account_id),
            admincredential=Utils.get_credential(admin_credential),
            yamlNewAccount=acc_yaml
        )
        lm_function = lambda request: self.lm_stub.newAccount(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.newAccountID)

    def get_account_id(self, account_name):

        request = logicmodule_messages_pb2.GetAccountIDRequest(
            accountName=account_name
        )
        lm_function = lambda request: self.lm_stub.getAccountID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.newAccountID)

    def get_account_list(self, admin_account_id, admin_credential):

        request = logicmodule_messages_pb2.GetAccountListRequest(
            adminID=Utils.get_msg_options['account'](admin_account_id),
            admincredential=Utils.get_credential(admin_credential)
        )
        lm_function = lambda request: self.lm_stub.getAccountList(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = set()

        for acc_id in response.accountIDs:
            result.add(Utils.get_id_from_uuid(acc_id))

        return result

    # Methods for Session Manager

    def new_session(self, account_id, credential, contracts, data_sets,
                    data_set_for_store, new_session_lang):

        contracts_list = []

        for con_id in contracts:
            contracts_list.append(Utils.get_msg_options['contract'](con_id))

        data_set_list = []
        for data_set in data_sets:
            data_set_list.append(data_set)

        request = logicmodule_messages_pb2.NewSessionRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            contractIDs=contracts_list,
            dataSets=data_set_list,
            storeDataSet=data_set_for_store,
            sessionLang=new_session_lang
        )
        lm_function = lambda request: self.lm_stub.newSession(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return dataclay_yaml_load(response.sessionInfo)

    def get_info_of_session_for_ds(self, session_id):

        request = logicmodule_messages_pb2.GetInfoOfSessionForDSRequest(
            sessionID=Utils.get_msg_options['session'](session_id)
        )
        lm_function = lambda request: self.lm_stub.getInfoOfSessionForDS(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        ds_id = Utils.get_id(response.dataSetID)

        calendar = datetime.fromtimestamp(response.date / 1e3).strftime('%Y-%m-%d %H:%M:%S')

        data_sets = set()

        for datas_id in response.dataSetIDs:
            data_sets.add(Utils.get_id(datas_id))

        t = (ds_id, data_sets), calendar
        return t

    # Methods for Namespace Manager

    def new_namespace(self, account_id, credential, namespace):

        yaml_dom = dataclay_yaml_dump(namespace)

        request = logicmodule_messages_pb2.NewNamespaceRequest(
            accountID=account_id,
            credential=Utils.get_credential(credential),
            newNamespaceYaml=yaml_dom
        )
        lm_function = lambda request: self.lm_stub.newNamespace(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.namespaceID)

    def remove_namespace(self, account_id, credential, namespace_name):

        request = logicmodule_messages_pb2.RemoveNamespaceRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespaceName=namespace_name
        )
        lm_function = lambda request: self.lm_stub.removeNamespace(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def get_namespace_id(self, account_id, credential, namespace_name):

        request = logicmodule_messages_pb2.GetNamespaceIDRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespaceName=namespace_name
        )
        lm_function = lambda request: self.lm_stub.getNamespaceID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.namespaceID)

    def get_object_dataset_id(self, session_id, oid):

        request = logicmodule_messages_pb2.GetObjectDataSetIDRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](oid)
        )
        lm_function = lambda request: self.lm_stub.getObjectDataSetID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.dataSetID)

    def import_interface(self, account_id, credential, namespace_id, contract_id, interface_id):

        request = logicmodule_messages_pb2.ImportInterfaceRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespaceID=Utils.get_msg_options['namespace'](namespace_id),
            contractID=Utils.get_msg_options['contract'](contract_id),
            interfaceID=Utils.get_msg_options['interface'](interface_id)
        )
        lm_function = lambda request: self.lm_stub.importInterface(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def import_contract(self, account_id, credential, namespace_id, contract_id):

        request = logicmodule_messages_pb2.ImportContractRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespaceID=Utils.get_msg_options['namespace'](namespace_id),
            contractID=Utils.get_msg_options['contract'](contract_id),
        )
        lm_function = lambda request: self.lm_stub.importContract(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def get_info_of_classes_in_namespace(self, account_id, credential, namespace_id):

        request = logicmodule_messages_pb2.GetInfoOfClassesInNamespaceRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespace_id=Utils.get_msg_options['namespace'](namespace_id)
        )
        lm_function = lambda request: self.lm_stub.getInfoOfClassesInNamespace(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.classesInfoMap.iteritems():
            clazz = dataclay_yaml_load(v)
            result[Utils.get_id_from_uuid(k)] = clazz

        return result

    def get_imported_classes_info_in_namespace(self, account_id, credential, namespace_id):

        request = logicmodule_messages_pb2.GetImportedClassesInfoInNamespaceRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespace_id=Utils.get_msg_options['namespace'](namespace_id)
        )
        lm_function = lambda request: self.lm_stub.getImportedClassesInfoInNamespace(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.importedClassesMap.iteritems():
            clazz = dataclay_yaml_load(v)
            result[Utils.get_id_from_uuid(k)] = clazz

        return result

    def get_classid_from_import(self, account_id, credential, namespace_id, class_name):

        request = logicmodule_messages_pb2.GetClassIDFromImportRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespace_id=Utils.get_msg_options['namespace'](namespace_id),
            className=class_name
        )
        lm_function = lambda request: self.lm_stub.getClassIDfromImport(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.classID)

    def get_classname_and_namespace_for_ds(self, class_id):
        
        request = logicmodule_messages_pb2.GetClassNameAndNamespaceForDSRequest(
            classID=Utils.get_msg_options['class'](class_id)
        )
        lm_function = lambda request: self.lm_stub.getClassNameAndNamespaceForDS(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return response.className, response.namespace

    # Methods for DataSet Manager

    def new_dataset(self, account_id, credential, dataset):
        ds_yaml = dataclay_yaml_dump(dataset)

        request = logicmodule_messages_pb2.NewDataSetRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            datasetYaml=ds_yaml
        )
        lm_function = lambda request: self.lm_stub.newDataSet(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.dataSetID)

    def remove_dataset(self, account_id, credential, dataset_name):

        request = logicmodule_messages_pb2.RemoveDataSetRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            dataSetName=dataset_name
        )
        lm_function = lambda request: self.lm_stub.removeDataSet(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def get_dataset_id(self, account_id, credential, dataset_name):

        request = logicmodule_messages_pb2.GetDataSetIDRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            dataSetName=dataset_name
        )
        lm_function = lambda request: self.lm_stub.getDataSetID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.dataSetID)

    # Methods for Class Manager

    def new_class(self, account_id, credential, language, new_classes):

        new_cl = {}

        for klass in new_classes:
            yaml_str = dataclay_yaml_dump(klass)
            new_cl[klass.name] = yaml_str

        request = logicmodule_messages_pb2.NewClassRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            language=language,
            newClasses=new_cl
        )
        lm_function = lambda request: self.lm_stub.newClass(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.newClasses.iteritems():
            result[k] = dataclay_yaml_load(v)

        return result

    def new_class_id(self, account_id, credential, class_name, language, new_classes):

        new_cl = {}

        for klass in new_classes:
            yaml_str = dataclay_yaml_dump(klass)
            new_cl[klass.name] = yaml_str

        request = logicmodule_messages_pb2.NewClassIDRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            language=language,
            className=class_name,
            newClasses=new_cl
        )
        lm_function = lambda request: self.lm_stub.newClassID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.classID)

    def new_enrichment(self, account_id, credential, namespace, class_name_to_be_enriched, language,
                       new_enrichments_specs):

        enr_spec = ()

        for k, v in new_enrichments_specs.iteritems():
            yaml_str = dataclay_yaml_dump(v)
            enr_spec = (k, yaml_str)

        request = logicmodule_messages_pb2.NewEnrichmentRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespace=namespace,
            classNameToBeEnriched=class_name_to_be_enriched,
            language=language,
            enrichmentsSpecs=enr_spec
        )
        lm_function = lambda request: self.lm_stub.newEnrichment(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        info = dataclay_yaml_load(response.enrichmentInfoYaml)

        result = dict()

        for k, v in response.newClassesMap.iteritems():
            clazz = dataclay_yaml_load(v)
            result[k] = clazz

        t = (info, result)

        return t

    def remove_class(self, account_id, credential, namespace_id, class_name):

        request = logicmodule_messages_pb2.RemoveClassRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            className=class_name
        )
        lm_function = lambda request: self.lm_stub.removeClass(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def remove_operation(self, account_id, credential, namespace_id, class_name, operation_signature):

        request = logicmodule_messages_pb2.RemoveOperationRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespace_id=Utils.get_msg_options['namespace'](namespace_id),
            className=class_name,
            operationNameAndSignature=operation_signature
        )
        lm_function = lambda request: self.lm_stub.removeOperation(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def remove_implementation(self, account_id, credential, namespace_id, implementation_id):

        request = logicmodule_messages_pb2.RemoveImplementationRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespace_id=Utils.get_msg_options['namespace'](namespace_id),
            implementationID=Utils.get_msg_options['implem'](implementation_id)
        )
        lm_function = lambda request: self.lm_stub.removeImplementation(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def get_operation_id(self, account_id, credential, namespace_id, class_name, operation_signature):

        request = logicmodule_messages_pb2.GetOperationIDRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespace_id=Utils.get_msg_options['namespace'](namespace_id),
            className=class_name,
            operationNameAndSignature=operation_signature
        )
        lm_function = lambda request: self.lm_stub.getOperationID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.operationID)

    def get_property_id(self, account_id, credential, namespace_id, class_name, property_name):

        request = logicmodule_messages_pb2.GetPropertyIDRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespaceID=Utils.get_msg_options['namespace'](namespace_id),
            className=class_name,
            propertyName=property_name
        )
        lm_function = lambda request: self.lm_stub.getPropertyID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.propertyID)

    def get_class_id(self, account_id, credential, namespace_id, class_name):

        request = logicmodule_messages_pb2.GetClassIDRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespaceID=Utils.get_msg_options['namespace'](namespace_id),
            className=class_name
        )
        lm_function = lambda request: self.lm_stub.getClassID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.classID)

    def get_class_info(self, account_id, credential, namespace_id, class_name):

        request = logicmodule_messages_pb2.GetClassInfoRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespace_id=Utils.get_msg_options['namespace'](namespace_id),
            className=class_name
        )
        lm_function = lambda request: self.lm_stub.getClassInfo(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return dataclay_yaml_load(response.metaClassYaml)

    def get_implementationids_that_meet_req(self, account_id, credential, operation_id, required_features):

        add_feat_yaml = None

        for f in required_features:
            add_feat_yaml = dataclay_yaml_dump(f)

        request = logicmodule_messages_pb2.GetImplIDsThatMeetReqRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            operationID=Utils.get_msg_options['operation'](operation_id),
            featuresYaml=add_feat_yaml
        )
        lm_function = lambda request: self.lm_stub.getImplementationIDsThatMeetReq(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for implid_str in response.implementationIDsList:
            result.update(Utils.get_id(implid_str))

        return result

    # Methods for Contract Manager

    def new_contract(self, account_id, credential, new_contract_s):

        yaml_contract = dataclay_yaml_dump(new_contract_s)

        request = logicmodule_messages_pb2.NewContractRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential,
            newContractYaml=yaml_contract
        )
        lm_function = lambda request: self.lm_stub.newContract(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.contractID)

    def register_to_public_contract(self, account_id, credential, contract_id):

        request = logicmodule_messages_pb2.RegisterToPublicContractRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential,
            contractID=Utils.get_msg_options['contract'](contract_id)
        )
        lm_function = lambda request: self.lm_stub.registerToPublicContract(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def get_contractids_of_applicant(self, applicant_account_id, credential):

        request = logicmodule_messages_pb2.GetContractIDsOfApplicantRequest(
            applicantID=Utils.get_msg_options['account'](applicant_account_id),
            credential=Utils.get_credential(credential)
        )
        lm_function = lambda request: self.lm_stub.getContractIDsOfApplicant(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.contracts.iteritems():
            result[Utils.get_id_from_uuid(k)] = dataclay_yaml_load(v)

        return result

    def get_contractids_of_provider(self, account_id, credential, namespaceid_of_provider):

        request = logicmodule_messages_pb2.GetDataContractIDsOfProviderRequest(
            providerID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespaceIDOfProvider=Utils.get_msg_options['namespace'](namespaceid_of_provider)
        )
        lm_function = lambda request: self.lm_stub.getContractIDsOfProvider(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.contracts.iteritems():
            result[Utils.get_id_from_uuid(k)] = dataclay_yaml_load(v)

        return result

    def get_contractids_of_applicant_with_provider(self, account_id, credential, namespaceid_of_provider):

        request = logicmodule_messages_pb2.GetContractsOfApplicantWithProvRequest(
            applicantID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespaceIDOfProvider=Utils.get_msg_options['namespace'](namespaceid_of_provider)
        )
        lm_function = lambda request: self.lm_stub.getContractIDsOfApplicantWithProvider(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.contracts.iteritems():
            result[Utils.get_id_from_uuid(k)] = dataclay_yaml_load(v)

        return result

    # Methods for DataContract Manager

    def new_data_contract(self, account_id, credential, new_datacontract):

        yaml_str = dataclay_yaml_dump(new_datacontract)

        request = logicmodule_messages_pb2.NewDataContractRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            dataContractYaml=yaml_str
        )
        lm_function = lambda request: self.lm_stub.newDataContract(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.dataContractID)

    def register_to_public_datacontract(self, account_id, credential, datacontract_id):

        request = logicmodule_messages_pb2.RegisterToPublicDataContractRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            dataContractID=Utils.get_msg_options['datacontract'](datacontract_id)
        )
        lm_function = lambda request: self.lm_stub.registerToPublicDataContract(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def get_datacontractids_of_provider(self, account_id, credential, datasetid_of_provider):

        request = logicmodule_messages_pb2.GetDataContractIDsOfProviderRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            dataSetIDOfProvider=Utils.get_msg_options['dataset'](datasetid_of_provider)
        )
        lm_function = lambda request: self.lm_stub.getDataContractIDsOfProvider(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.datacontracts.iteritems():
            result[Utils.get_id_from_uuid(k)] = dataclay_yaml_load(v)

        return result

    def get_datacontractids_of_applicant(self, applicant_accountid, credential):

        request = logicmodule_messages_pb2.GetDataContractIDsOfApplicantRequest(
            applicantID=Utils.get_msg_options['account'](applicant_accountid),
            credential=Utils.get_credential(credential)
        )
        lm_function = lambda request: self.lm_stub.getDataContractIDsOfApplicant(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.datacontracts.iteritems():
            result[Utils.get_id_from_uuid(k)] = dataclay_yaml_load(v)

        return result

    def get_datacontract_info_of_applicant_with_provider(self, applicant_accountid, credential, datasetid_of_provider):

        request = logicmodule_messages_pb2.GetDataContractInfoOfApplicantWithProvRequest(
            applicantID=Utils.get_msg_options['account'](applicant_accountid),
            credential=Utils.get_credential(credential),
            dataSetIDOfProvider=Utils.get_msg_options['dataset'](datasetid_of_provider)
        )
        lm_function = lambda request: self.lm_stub.getDataContractInfoOfApplicantWithProvider(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return dataclay_yaml_load(response.dataContractInfo)

    # Methods for Interface Manager

    def new_interface(self, account_id, credential, new_interface_s):

        yaml_str = dataclay_yaml_dump(new_interface_s)

        request = logicmodule_messages_pb2.NewInterfaceRequest(
            applicantID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            interfaceYaml=yaml_str
        )
        lm_function = lambda request: self.lm_stub.newInterface(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.interfaceID)

    def get_interface_info(self, account_id, credential, interface_id):

        request = logicmodule_messages_pb2.GetInterfaceInfoRequest(
            applicantID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            interfaceID=Utils.get_msg_options['interface'](interface_id)
        )
        lm_function = lambda request: self.lm_stub.getInterfaceInfo(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return dataclay_yaml_load(response.interfaceYaml)

    def remove_interface(self, account_id, credential, namespace_id, interface_id):

        request = logicmodule_messages_pb2.RemoveInterfaceRequest(
            applicantID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            namespaceID=Utils.get_msg_options['namespace'](namespace_id),
            interfaceID=Utils.get_msg_options['interface'](interface_id)
        )
        lm_function = lambda request: self.lm_stub.removeInterface(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    # Methods for MetaDataService for DS

    def get_storage_locationid_for_ds(self, ds_name):

        request = logicmodule_messages_pb2.GetStorageLocationIDForDSRequest(
            dsName=ds_name
        )
        lm_function = lambda request: self.lm_stub.getStorageLocationIDForDS(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.storageLocationID)

    def get_storage_location_for_ds(self, st_loc_id):

        request = logicmodule_messages_pb2.GetStorageLocationForDSRequest(
            storageLocationID=Utils.get_msg_options['storage_loc'](st_loc_id)
        )
        lm_function = lambda request: self.lm_stub.getStorageLocationForDS(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return dataclay_yaml_load(response.storageLocationYaml)

    def get_executionenvironmentid_for_ds(self, ds_name, ds_lang):

        request = logicmodule_messages_pb2.GetExecutionEnvironmentIDForDSRequest(
            dsName=ds_name,
            execEnvLang=ds_lang
        )
        lm_function = lambda request: self.lm_stub.getExecutionEnvironmentIDForDS(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.execEnvID)

    def get_executionenvironment_for_ds(self, backend_id):

        request = logicmodule_messages_pb2.GetExecutionEnvironmentForDSRequest(
            execEnvID=Utils.get_msg_options['exec_env'](backend_id)
        )
        lm_function = lambda request: self.lm_stub.getExecutionEnvironmentForDS(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return dataclay_yaml_load(response.execEnvYaml)

    def get_federation_of_object(self, object_id):
        request = logicmodule_messages_pb2.GetFederationOfObjectRequest(
            objectID=Utils.get_msg_options['object'](object_id)
        )
        lm_function = lambda request: self.lm_stub.getFederationOfObject(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = set()

        for ext_dataclay_yaml in response.extDataClayYamlsList:
            result.add(dataclay_yaml_load(ext_dataclay_yaml))
        
        return result

    def register_objects_from_ds_garbage_collector(self, reg_info, backend_id):

        reg_info_set = CommonMessages.RegistrationInfo(
            objectID=Utils.get_msg_options['object'](reg_info[0]),
            classID=Utils.get_msg_options['meta_class'](reg_info[1]),
            sessionID=Utils.get_msg_options['session'](reg_info[2]),
            dataSetID=Utils.get_msg_options['dataset'](reg_info[3])
        )

        request = logicmodule_messages_pb2.RegisterObjectsForDSRequest(
            regInfo=reg_info_set,
            backendID=Utils.get_msg_options['backend_id'](backend_id)
        )

        # ToDo: In Java at this point override the onNext/onError/onCompleted methods of responseObserver
        """
        try:
            logger.trace("Asynchronous call to register object from Garbage Collector for object %s",
                         reg_info[0])

            # ToDo: check async
            async_req_send.next()

            resp_future = self.lm_stub.registerObjectsFromDSGarbageCollector.future(request, timeout=TIME_OUT)

            resp_future.result()

            if resp_future.done():
                async_req_rec.next()

        except RuntimeError as e:
            raise e
        
        if resp_future.isException:
            raise DataclayException(resp_future.exceptionMessage)
        """ 
        lm_function = lambda request: self.lm_stub.registerObjectsFromDSGarbageCollector(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)

        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def register_objects(self, reg_infos, backend_id, object_id_to_have_alias, alias, lang):

        reg_info_b = list()

        for reg_info in reg_infos:
            reg_info_b.append(CommonMessages.RegistrationInfo(
                objectID=Utils.get_msg_options['object'](reg_info[0]),
                classID=Utils.get_msg_options['meta_class'](reg_info[1]),
                sessionID=Utils.get_msg_options['session'](reg_info[2]),
                dataSetID=Utils.get_msg_options['dataset'](reg_info[3])
                )
            )

        if object_id_to_have_alias is not None:

            request = logicmodule_messages_pb2.RegisterObjectsRequest(
                regInfo=reg_info_b,
                backendID=Utils.get_msg_options['backend_id'](backend_id),
                objectIDToHaveAlias=Utils.get_msg_options['object'](object_id_to_have_alias),
                alias=alias,
                lang=common_messages_pb2.LANG_PYTHON
            )

        else:

            request = logicmodule_messages_pb2.RegisterObjectsRequest(
                regInfo=reg_info_b,
                backendID=Utils.get_msg_options['backend_id'](backend_id),
                lang=common_messages_pb2.LANG_PYTHON
            )
        lm_function = lambda request: self.lm_stub.registerObjects(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def set_dataset_id_from_garbage_collector(self, object_id, dataset_id):

        request = logicmodule_messages_pb2.SetDataSetIDFromGarbageCollectorRequest(
            objectID=Utils.get_msg_options['object'](object_id),
            datasetID=Utils.get_msg_options['dataset'](dataset_id)
        )

        # ToDo: In Java at this point override the onNext/onError/onCompleted methods of responseObserver

        try:
            logger.trace("Asynchronous call to register object from Garbage Collector for object %s",
                         object_id)

            # ToDo: check async
            async_req_send.next()

            resp_future = self.lm_stub.setDataSetIDFromGarbageCollector.future(request, timeout=TIME_OUT)

            resp_future.result()

            if resp_future.done():
                async_req_rec.next()

        except RuntimeError as e:
            raise e

        if resp_future.isException:
            raise DataclayException(resp_future.exceptionMessage)

    # Methods for MetaDataService

    def get_execution_environment_info(self, session_id, exec_location_id):

        request = logicmodule_messages_pb2.GetExecutionEnvironmentInfoRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            execLocID=Utils.get_msg_options['exec_env'](exec_location_id)
        )
        lm_function = lambda request: self.lm_stub.getExecutionEnvironmentInfo(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return dataclay_yaml_load(response.execLocationYaml)

    def get_dataclay_id(self):
        
        lm_function = lambda request: self.lm_stub.getDataClayID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(CommonMessages.EmptyMessage(), lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.exceptionMessage)

        return Utils.get_id(response.dataClayID)

    def federate_object(self, session_id, object_id, ext_dataclay_name, recursive):
        request = logicmodule_messages_pb2.FederateObjectRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](object_id),
            extDataClayName=ext_dataclay_name,
            recursive=recursive
        )
        lm_function = lambda request: self.lm_stub.federateObject(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def check_object_is_federated_with_dataclay_instance(self, object_id, ext_dataclay_id):
        request = logicmodule_messages_pb2.CheckObjectFederatedWithDataClayInstanceRequest(
            objectID=Utils.get_msg_options['object'](object_id),
            extDataClayID=Utils.get_msg_options['dataclay_instance'](ext_dataclay_id)
        )
        lm_function = lambda request: self.lm_stub.checkObjectIsFederatedWithDataClayInstance(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.exceptionMessage)

        return response.isFederated

    def get_storage_location_id(self, account_id, credential, st_loc_name):

        request = logicmodule_messages_pb2.GetStorageLocationIDRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            stLocName=st_loc_name
        )
        lm_function = lambda request: self.lm_stub.getStorageLocationID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.storageLocationID)

    def get_execution_environment_id(self, account_id, credential, exe_env_name, exe_env_lang):

        request = logicmodule_messages_pb2.GetExecutionEnvironmentIDRequest(
            accountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            locName=exe_env_name,
            execEnvLang=exe_env_lang
        )
        lm_function = lambda request: self.lm_stub.getExecutionEnvironmentID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.execEnvID)

    def get_storage_location_info(self, session_id, st_loc_id):

        request = logicmodule_messages_pb2.GetStorageLocationInfoRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            stLocID=Utils.get_msg_options['storage_loc'](st_loc_id)
        )
        lm_function = lambda request: self.lm_stub.getStorageLocationInfo(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return dataclay_yaml_load(response.stLocationYaml)

    def get_storage_locations_info(self, session_id):

        request = logicmodule_messages_pb2.GetStorageLocationsInfoRequest(
            sessionID=Utils.get_msg_options['session'](session_id)
        )
        lm_function = lambda request: self.lm_stub.getStorageLocationsInfo(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.storageLocations.iteritems():
            result[Utils.get_id_from_uuid(k)] = dataclay_yaml_load(v)

        return result

    def get_execution_environments_info(self, session_id, language):

        request = logicmodule_messages_pb2.GetExecutionEnvironmentsInfoRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            execEnvLang=language
        )
        lm_function = lambda request: self.lm_stub.getExecutionEnvironmentsInfo(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.execEnvs.iteritems():
            result[Utils.get_id_from_uuid(k)] = dataclay_yaml_load(v)

        return result

    def get_execution_environments_per_locations(self, session_id, exe_env_lang):

        request = logicmodule_messages_pb2.GetExecutionEnvironmentsPerLocationsRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            execEnvLang=exe_env_lang
        )
        lm_function = lambda request: self.lm_stub.getExecutionEnvironmentsPerLocations(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.locsPerExec.iteritems():
            result[Utils.get_id_from_uuid(k)] = Utils.get_id_from_uuid(v)

        return result

    def get_execution_environments_per_locations_for_ds(self, exe_env_lang):

        request = logicmodule_messages_pb2.GetExecutionEnvironmentsPerLocationsForDSRequest(
            execEnvLang=exe_env_lang
        )
        lm_function = lambda request: self.lm_stub.getExecutionEnvironmentsPerLocationsForDS(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.locsPerExec.iteritems():
            result[Utils.get_id_from_uuid(k)] = Utils.get_id_from_uuid(v)

        return result

    def get_storage_locations_per_execution_environments(self, session_id, exe_env_lang):

        request = logicmodule_messages_pb2.GetStorageLocationsPerExecutionEnvironmentsRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            execEnvLang=exe_env_lang
        )
        lm_function = lambda request: self.lm_stub.getStorageLocationsPerExecutionEnvironments(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.locsPerExec.iteritems():
            result[Utils.get_id_from_uuid(v)] = Utils.get_id_from_uuid(k)

        return result

    def get_object_info(self, session_id, object_id):

        request = logicmodule_messages_pb2.GetObjectInfoRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](object_id)
        )
        lm_function = lambda request: self.lm_stub.getObjectInfo(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return response.classname, response.namespace

    def get_object_from_alias(self, session_id, metaclass_id, alias):

        request = logicmodule_messages_pb2.GetObjectFromAliasRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            classID=Utils.get_msg_options['meta_class'](metaclass_id),
            alias=alias
        )
        lm_function = lambda request: self.lm_stub.getObjectFromAlias(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        t = (Utils.get_id(response.objectID), Utils.get_id(response.hint))

        return t

    def delete_alias(self, session_id, metaclass_id, alias):

        request = logicmodule_messages_pb2.DeleteAliasRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            classID=Utils.get_msg_options['meta_class'](metaclass_id),
            alias=alias
        )
        lm_function = lambda request: self.lm_stub.deleteAlias(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.excInfo.exceptionMessage)
        
    def get_objects_metadata_info_of_class_for_nm(self, class_id):

        request = logicmodule_messages_pb2.GetObjectsMetaDataInfoOfClassForNMRequest(
            classID=Utils.get_msg_options['meta_class'](class_id)
        )
        lm_function = lambda request: self.lm_stub.getObjectsMetaDataInfoOfClassForNM(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.mdataInfo:
            result[Utils.get_id_from_uuid(k)] = dataclay_yaml_load(v)

        return result

    # Methods for Storage Location

    def set_dataset_id(self, session_id, object_id, dataset_id):

        request = logicmodule_messages_pb2.SetDataSetIDRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](object_id),
            datasetID=Utils.get_msg_options['dataset'](dataset_id)
        )
        lm_function = lambda request: self.lm_stub.setDataSetID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def make_persistent(self, session_id, dest_backend_id, serialized_objects,
                        ds_specified, object_to_have_alias, alias):

        obj_data = list()

        for vol_obj in serialized_objects:
            obj_data.append(Utils.get_obj_with_data_param_or_return(vol_obj))

        ds_msg = dict()
        for k, v in ds_specified.iteritems():
            # ToDo: check it
            ds_msg[str(k)] = Utils.get_msg_options['dataset'](v)

        request = logicmodule_messages_pb2.MakePersistentRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            backendID=Utils.get_msg_options['backend_id'](dest_backend_id),
            objects=obj_data,
            datasetsSpecified=ds_msg,
            objectIDToHaveAlias=Utils.get_msg_options['object'](object_to_have_alias),
            oidAlias=alias
        )

        # ToDo: Complete the method with if Configuration.Flags.UseSyncMkPers.getBoolean else
        # For the moment simply ignore it

        # ToDo: For the moment all call are considered synchronous
        config = True

        if config:
            try:
                if logger.isEnabledFor(logging.TRACE):
                    objs_to_reg = []

                    for reg_info in serialized_objects:
                        objs_to_reg.append(reg_info[0])

                    logger.trace("Synchronous MakePersistent call of objects: %s",
                                 objs_to_reg)
                logger.verbose("Calling make persistent")
                lm_function = lambda request: self.lm_stub.makePersistent(request, timeout=TIME_OUT)
                response = self._call_logicmodule(request, lm_function)

            except RuntimeError as e:
                raise e

            if response.isException:
                raise DataclayException(response.exceptionMessage)

        else:
            try:
                # ToDo: In Java at this point override the onNext/onError/onCompleted methods of responseObserver
                if logger.isEnabledFor(logging.TRACE):
                    # ToDo: objs_to_reg need to be an ObjectID of serialized_objects.size or maybe a list?
                    objs_to_reg = dict()
                    i = 0
                    for reg_info in serialized_objects:
                        objs_to_reg[i] = reg_info.objectID
                        i += 1

                    logger.trace("Asynchronous MakePersistent call of objects: %s",
                                 objs_to_reg)

                # ToDo: check async

                async_req_send.next()

                logger.verbose("Calling make persistent with future")
                resp_future = self.lm_stub.makePersistent.future(request, timeout=TIME_OUT)

                resp_future.result()

                if resp_future.done():
                    async_req_rec.next()

            except RuntimeError as e:
                raise e

    def new_version(self, session_id, object_id, optional_dest_backend_id):

        request = logicmodule_messages_pb2.NewVersionRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](object_id),
            optDestBackendID=Utils.get_msg_options['backend_id'](optional_dest_backend_id)
        )
        lm_function = lambda request: self.lm_stub.newVersion(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        # ToDo: Correct the return (Return only dataclay_yaml_load(..))
        return dataclay_yaml_load(response.versionInfoYaml), response.versionInfoYaml

    def consolidate_version(self, session_id, version):

        request = logicmodule_messages_pb2.ConsolidateVersionRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            # ToDo: Correct versionInfoYaml with the commented one
            # versionInfoYaml=dataclay_yaml_dump(version)
            versionInfoYaml=version
        )
        lm_function = lambda request: self.lm_stub.consolidateVersion(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def new_replica(self, session_id, object_id, backend_id, recursive):

        request = logicmodule_messages_pb2.NewReplicaRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](object_id),
            destBackendID=Utils.get_msg_options['backend_id'](backend_id),
            recursive=recursive
        )
        lm_function = lambda request: self.lm_stub.newReplica(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.destBackendID)

    def move_object(self, session_id, object_id, src_backend_id, dest_backend_id, recursive):

        request = logicmodule_messages_pb2.MoveObjectRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](object_id),
            srcBackendID=Utils.get_msg_options['backend_id'](src_backend_id),
            destBackendID=Utils.get_msg_options['backend_id'](dest_backend_id),
            recursive=recursive
        )
        lm_function = lambda request: self.lm_stub.moveObject(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)
        
    def set_object_read_only(self, session_id, object_id):

        request = logicmodule_messages_pb2.SetObjectReadOnlyRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](object_id)
        )
        lm_function = lambda request: self.lm_stub.setObjectReadOnly(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def set_object_read_write(self, session_id, object_id):

        request = logicmodule_messages_pb2.SetObjectReadWriteRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](object_id)
        )
        lm_function = lambda request: self.lm_stub.setObjectReadWrite(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def get_metadata_by_oid(self, session_id, object_id):

        request = logicmodule_messages_pb2.GetMetadataByOIDRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](object_id)
        )
        lm_function = lambda request: self.lm_stub.getMetadataByOID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return dataclay_yaml_load(response.objMdataYaml)

    # Methods for Execution Environment

    def execute_implementation(self, session_id, operation_id, remote_implementation, object_id, params):

        request = logicmodule_messages_pb2.ExecuteImplementationRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            operationID=Utils.get_msg_options['operation'](operation_id),
            implementationID=Utils.get_msg_options['implem'](remote_implementation[0]),
            contractID=Utils.get_msg_options['contract'](remote_implementation[1]),
            interfaceID=Utils.get_msg_options['interface'](remote_implementation[2]),
            params=Utils.get_param_or_return(params),
            objectID=Utils.get_msg_options['object'](object_id)
        )
        lm_function = lambda request: self.lm_stub.executeImplementation(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        if response.ret is not None:
            return Utils.get_param_or_return(response.ret)
        else:
            return None

    def execute_method_on_target(self, session_id, object_id, operation_signature, params, backend_id):

        request = logicmodule_messages_pb2.ExecuteMethodOnTargetRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            objectID=Utils.get_msg_options['object'](object_id),
            operationNameAndSignature=operation_signature,
            params=Utils.get_param_or_return(params),
            targetBackendID=Utils.get_msg_options['backend_id'](backend_id)
        )
        lm_function = lambda request: self.lm_stub.executeMethodOnTarget(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        if 'response.ret' in globals() or 'response.ret' in locals():
            return Utils.get_param_or_return(response.ret)

        else:
            return None

    def execute_on_federated_objects(self, dataclay_id, object_id, impl_info, params):
        
        if params is not None:
            request = logicmodule_messages_pb2.ExecuteOnFederatedObjectRequest(
                extDataClayID=Utils.get_msg_options['dataclay_instance'](dataclay_id),
                objectID=Utils.get_msg_options['object'](object_id),
                allImplInfo=impl_info,
                params=Utils.get_param_or_return(params)
            )
        else:
            request = logicmodule_messages_pb2.ExecuteOnFederatedObjectRequest(
                extDataClayID=Utils.get_msg_options['dataclay_instance'](dataclay_id),
                objectID=Utils.get_msg_options['object'](object_id),
                allImplInfo=impl_info
            )
        
        lm_function = lambda request: self.lm_stub.executeOnFederatedObject(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)

        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        if response.ret is not None:
            return Utils.get_param_or_return(response.ret) 
        else:
            return None

    # Methods for Stubs

    def get_stubs(self, applicant_account_id, applicant_credential, language, contracts_ids):

        cid_list = []

        for cID in contracts_ids:
            cid_list.append(Utils.get_msg_options['contract'](cID))

        request = logicmodule_messages_pb2.GetStubsRequest(
            applicantAccountID=Utils.get_msg_options['account'](applicant_account_id),
            credentials=Utils.get_credential(applicant_credential),
            language=language,
            contractIDs=cid_list
        )
        lm_function = lambda request: self.lm_stub.getStubs(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        result = dict()

        for k, v in response.stubs.iteritems():
            result[k] = bytes(v)

        return result

    def get_babel_stubs(self, applicant_account_id, applicant_credential, contracts_ids):

        cid_list = []

        for cID in contracts_ids:
            cid_list.append(Utils.get_msg_options['contract'](cID))

        request = logicmodule_messages_pb2.GetBabelStubsRequest(
            accountID=Utils.get_msg_options['account'](applicant_account_id),
            credentials=Utils.get_credential(applicant_credential),
            contractIDs=cid_list
        )
        lm_function = lambda request: self.lm_stub.getBabelStubs(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return response.yamlStub

    # Notification Manager Methods

    def register_event_listener_implementation(self, account_id, credential, new_event_listener):

        request = logicmodule_messages_pb2.RegisterECARequest(
            applicantAccountID=Utils.get_msg_options['account'](account_id),
            credentials=Utils.get_credential(credential),
            eca=dataclay_yaml_dump(new_event_listener)
        )
        lm_function = lambda request: self.lm_stub.registerECA(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

    def register_listener_persisted_object_with_class_name(self, account_id, credential, producer_event_class_name,
                                                           target_metaclass_id, filter_method,
                                                           target_obj_method_to_invoke):

        request = logicmodule_messages_pb2.RegisterListenerObjectWithClassNameRequest(
            accID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            producerEventClassName=producer_event_class_name,
            targetMetaClassID=Utils.get_msg_options['meta_class'](target_metaclass_id),
            filterMethod=Utils.get_msg_options['operation'](filter_method),
            targetObjectMethodToInvoke=Utils.get_msg_options['operation'](target_obj_method_to_invoke)
        )
        lm_function = lambda request: self.lm_stub.registerListenerPersistedObjectWithClassName(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def register_listener_persisted_object_with_object_id(self, account_id, credential, producer_event_object_id,
                                                          target_metaclass_id, filter_method,
                                                          target_obj_method_to_invoke):

        request = logicmodule_messages_pb2.RegisterListenerObjectWithObjectIDRequest(
            accID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            objectID=Utils.get_msg_options['object'](producer_event_object_id),
            targetMetaClassID=Utils.get_msg_options['meta_class'](target_metaclass_id),
            filterMethod=Utils.get_msg_options['operation'](filter_method),
            targetObjectMethodToInvoke=Utils.get_msg_options['operation'](target_obj_method_to_invoke)
        )
        lm_function = lambda request: self.lm_stub.registerListenerPersistedObjectWithObjectID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def register_listener_deleted_object_with_class_name(self, account_id, credential, producer_event_class_name,
                                                         target_metaclass_id, filter_method,
                                                         target_obj_method_to_invoke):

        request = logicmodule_messages_pb2.RegisterListenerDeletedObjectWithClassNameRequest(
            accID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            producerEventClassName=producer_event_class_name,
            targetMetaClassID=Utils.get_msg_options['meta_class'](target_metaclass_id),
            filterMethod=Utils.get_msg_options['operation'](filter_method),
            targetObjectMethodToInvoke=Utils.get_msg_options['operation'](target_obj_method_to_invoke)
        )
        lm_function = lambda request: self.lm_stub.registerListenerDeletedObjectWithClassName(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def register_listener_deleted_object_with_object_id(self, account_id, credential, producer_event_object_id,
                                                        target_metaclass_id, filter_method,
                                                        target_obj_method_to_invoke):

        request = logicmodule_messages_pb2.RegisterListenerDeletedObjectWithObjectIDRequest(
            accID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential),
            objectID=Utils.get_msg_options['object'](producer_event_object_id),
            targetMetaClassID=Utils.get_msg_options['meta_class'](target_metaclass_id),
            filterMethod=Utils.get_msg_options['operation'](filter_method),
            targetObjectMethodToInvoke=Utils.get_msg_options['operation'](target_obj_method_to_invoke)
        )
        lm_function = lambda request: self.lm_stub.registerListenerDeletedObjectWithObjectID(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def advise_event(self, new_event):

        request = logicmodule_messages_pb2.AdviseEventRequest(
            eventYaml=dataclay_yaml_dump(new_event)
        )
        lm_function = lambda request: self.lm_stub.adviseEvent(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    # Others Methods

    def get_class_name_for_ds(self, class_id):

        request = logicmodule_messages_pb2.GetClassNameForDSRequest(
            classID=Utils.get_msg_options['meta_class'](class_id)
        )
        lm_function = lambda request: self.lm_stub.getClassNameForDS(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return response.className

    def get_class_name_and_namespace_for_ds(self, class_id):

        request = logicmodule_messages_pb2.GetClassNameAndNamespaceForDSRequest(
            classID=Utils.get_msg_options['meta_class'](class_id)
        )
        lm_function = lambda request: self.lm_stub.getClassNameAndNamespaceForDS(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        t = (response.className, response.namespace)

        return t

    def get_contract_id_of_dataclay_provider(self, account_id, credential):

        request = logicmodule_messages_pb2.GetContractIDOfDataClayProviderRequest(
            applicantAccountID=Utils.get_msg_options['account'](account_id),
            credential=Utils.get_credential(credential)
        )
        lm_function = lambda request: self.lm_stub.getContractIDOfDataClayProvider(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return Utils.get_id(response.contractID)

    # Garbage Collector Methods

    def close_session(self, session_id):

        request = logicmodule_messages_pb2.CloseSessionRequest(
            sessionID=Utils.get_msg_options['session'](session_id)
        )
        lm_function = lambda request: self.lm_stub.closeSession(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    # Paraver Methods

    def create_paraver_traces(self):
        lm_function = lambda request: self.lm_stub.createParaverTraces(request, timeout=TIME_OUT)
        try:
            response = self._call_logicmodule(CommonMessages.EmptyMessage(), lm_function)
        except RuntimeError as e:
            return 0
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def activate_tracing(self):
        lm_function = lambda request: self.lm_stub.activateTracing(request, timeout=TIME_OUT)
        try:
            response = self._call_logicmodule(CommonMessages.EmptyMessage(), lm_function)
        except RuntimeError as e:
            return 0

        if response.excInfo.isException:
            raise DataclayException(response.excInfo.exceptionMessage)

        return response.millis

    def deactivate_tracing(self):
        lm_function = lambda request: self.lm_stub.deactivateTracing(request, timeout=TIME_OUT)
        try:
            response = self._call_logicmodule(CommonMessages.EmptyMessage(), lm_function)
        except RuntimeError as e:
            raise e

        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def clean_metadata_caches(self):
        lm_function = lambda request: self.lm_stub.cleanMetaDataCaches(request, timeout=TIME_OUT)
        response = self._call_logicmodule(CommonMessages.EmptyMessage(), lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def close_manager_db(self):
        lm_function = lambda request: self.lm_stub.closeManagerDb(request, timeout=TIME_OUT)
        response = self._call_logicmodule(CommonMessages.EmptyMessage(), lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def close_db(self):
        lm_function = lambda request: self.lm_stub.closeDb(request, timeout=TIME_OUT)
        response = self._call_logicmodule(CommonMessages.EmptyMessage(), lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def wait_and_process_async_req(self):
        # ToDo: wait all the async requests in a proper way

        while async_req_send != async_req_rec:
            try:
                return
            except NotImplementedError as e:
                raise Exception(e.message)

    def add_alias(self, session_id, metaclass_id, dest_backend_id,
                  object_id_to_have_alias, alias):
        
        request = logicmodule_messages_pb2.AddAliasRequest(
            sessionID=Utils.get_msg_options['session'](session_id),
            metaClassID=Utils.get_msg_options['meta_class'](metaclass_id) ,
            backendID=Utils.get_msg_options['exec_env'](dest_backend_id) ,
            objectIDToHaveAlias=Utils.get_msg_options['object'](object_id_to_have_alias),
            alias=alias
        )
        lm_function = lambda request: self.lm_stub.addAlias(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def notify_leader(self, hostname, host_port):

        request = logicmodule_messages_pb2.NotifyLMLeaderRequest(
            host=hostname,
            port=host_port,
        )
        lm_function = lambda request: self.lm_stub.notifyLMLeader(request, timeout=TIME_OUT)
        response = self._call_logicmodule(request, lm_function)
        if response.isException:
            raise DataclayException(response.exceptionMessage)

    def get_backup_info(self):
        lm_function = lambda request: self.lm_stub.getBackupInfo(request, timeout=TIME_OUT)
        response = self._call_logicmodule(CommonMessages.EmptyMessage(), lm_function)
        if response.excInfo.isException:
            raise DataclayException(response.exceptionMessage)
        return response.host, response.port

