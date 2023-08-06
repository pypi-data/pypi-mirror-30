#!/usr/bin/env python

#
# Generated Sun Apr 15 08:31:05 2018 by generateDS.py version 2.29.11.
# Python 2.7.14 (default, Mar 14 2018, 13:36:31)  [GCC 7.3.1 20180303 (Red Hat 7.3.1-5)]
#
# Command line options:
#   ('-q', '')
#   ('-f', '')
#   ('-o', 'pyone/bindings/supbind.py')
#   ('-s', 'pyone/bindings/__init__.py')
#   ('--super', 'supbind')
#   ('--external-encoding', 'utf-8')
#   ('--silence', '')
#
# Command line arguments:
#   pyone/xsd/index.xsd
#
# Command line:
#   /home/rafael/Development/privaz.io/python/env/bin/generateDS -q -f -o "pyone/bindings/supbind.py" -s "pyone/bindings/__init__.py" --super="supbind" --external-encoding="utf-8" --silence pyone/xsd/index.xsd
#
# Current working directory (os.getcwd()):
#   pyone
#

import sys
from pyone.util import TemplatedType
from lxml import etree as etree_

from . import supbind as supermod

def parsexml_(infile, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        parser = etree_.ETCompatXMLParser()
    doc = etree_.parse(infile, parser=parser, **kwargs)
    return doc

#
# Globals
#

ExternalEncoding = 'utf-8'

#
# Data representation classes
#


class HISTORY_RECORDSSub(TemplatedType, supermod.HISTORY_RECORDS):
    def __init__(self, HISTORY=None):
        super(HISTORY_RECORDSSub, self).__init__(HISTORY, )
supermod.HISTORY_RECORDS.subclass = HISTORY_RECORDSSub
# end class HISTORY_RECORDSSub


class HISTORYSub(TemplatedType, supermod.HISTORY):
    def __init__(self, OID=None, SEQ=None, HOSTNAME=None, HID=None, CID=None, STIME=None, ETIME=None, VM_MAD=None, TM_MAD=None, DS_ID=None, PSTIME=None, PETIME=None, RSTIME=None, RETIME=None, ESTIME=None, EETIME=None, ACTION=None, UID=None, GID=None, REQUEST_ID=None, VM=None):
        super(HISTORYSub, self).__init__(OID, SEQ, HOSTNAME, HID, CID, STIME, ETIME, VM_MAD, TM_MAD, DS_ID, PSTIME, PETIME, RSTIME, RETIME, ESTIME, EETIME, ACTION, UID, GID, REQUEST_ID, VM, )
supermod.HISTORY.subclass = HISTORYSub
# end class HISTORYSub


class CLUSTER_POOLSub(TemplatedType, supermod.CLUSTER_POOL):
    def __init__(self, CLUSTER=None):
        super(CLUSTER_POOLSub, self).__init__(CLUSTER, )
supermod.CLUSTER_POOL.subclass = CLUSTER_POOLSub
# end class CLUSTER_POOLSub


class CLUSTERSub(TemplatedType, supermod.CLUSTER):
    def __init__(self, ID=None, NAME=None, HOSTS=None, DATASTORES=None, VNETS=None, TEMPLATE=None):
        super(CLUSTERSub, self).__init__(ID, NAME, HOSTS, DATASTORES, VNETS, TEMPLATE, )
supermod.CLUSTER.subclass = CLUSTERSub
# end class CLUSTERSub


class DATASTORE_POOLSub(TemplatedType, supermod.DATASTORE_POOL):
    def __init__(self, DATASTORE=None):
        super(DATASTORE_POOLSub, self).__init__(DATASTORE, )
supermod.DATASTORE_POOL.subclass = DATASTORE_POOLSub
# end class DATASTORE_POOLSub


class DATASTORESub(TemplatedType, supermod.DATASTORE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, DS_MAD=None, TM_MAD=None, BASE_PATH=None, TYPE=None, DISK_TYPE=None, STATE=None, CLUSTERS=None, TOTAL_MB=None, FREE_MB=None, USED_MB=None, IMAGES=None, TEMPLATE=None):
        super(DATASTORESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, DS_MAD, TM_MAD, BASE_PATH, TYPE, DISK_TYPE, STATE, CLUSTERS, TOTAL_MB, FREE_MB, USED_MB, IMAGES, TEMPLATE, )
supermod.DATASTORE.subclass = DATASTORESub
# end class DATASTORESub


class GROUP_POOLSub(TemplatedType, supermod.GROUP_POOL):
    def __init__(self, GROUP=None, QUOTAS=None, DEFAULT_GROUP_QUOTAS=None):
        super(GROUP_POOLSub, self).__init__(GROUP, QUOTAS, DEFAULT_GROUP_QUOTAS, )
supermod.GROUP_POOL.subclass = GROUP_POOLSub
# end class GROUP_POOLSub


class GROUPSub(TemplatedType, supermod.GROUP):
    def __init__(self, ID=None, NAME=None, TEMPLATE=None, USERS=None, ADMINS=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, DEFAULT_GROUP_QUOTAS=None):
        super(GROUPSub, self).__init__(ID, NAME, TEMPLATE, USERS, ADMINS, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, DEFAULT_GROUP_QUOTAS, )
supermod.GROUP.subclass = GROUPSub
# end class GROUPSub


class HOST_POOLSub(TemplatedType, supermod.HOST_POOL):
    def __init__(self, HOST=None):
        super(HOST_POOLSub, self).__init__(HOST, )
supermod.HOST_POOL.subclass = HOST_POOLSub
# end class HOST_POOLSub


class HOSTSub(TemplatedType, supermod.HOST):
    def __init__(self, ID=None, NAME=None, STATE=None, IM_MAD=None, VM_MAD=None, LAST_MON_TIME=None, CLUSTER_ID=None, CLUSTER=None, HOST_SHARE=None, VMS=None, TEMPLATE=None):
        super(HOSTSub, self).__init__(ID, NAME, STATE, IM_MAD, VM_MAD, LAST_MON_TIME, CLUSTER_ID, CLUSTER, HOST_SHARE, VMS, TEMPLATE, )
supermod.HOST.subclass = HOSTSub
# end class HOSTSub


class IMAGE_POOLSub(TemplatedType, supermod.IMAGE_POOL):
    def __init__(self, IMAGE=None):
        super(IMAGE_POOLSub, self).__init__(IMAGE, )
supermod.IMAGE_POOL.subclass = IMAGE_POOLSub
# end class IMAGE_POOLSub


class IMAGESub(TemplatedType, supermod.IMAGE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, TYPE=None, DISK_TYPE=None, PERSISTENT=None, REGTIME=None, SOURCE=None, PATH=None, FSTYPE=None, SIZE=None, STATE=None, RUNNING_VMS=None, CLONING_OPS=None, CLONING_ID=None, TARGET_SNAPSHOT=None, DATASTORE_ID=None, DATASTORE=None, VMS=None, CLONES=None, APP_CLONES=None, TEMPLATE=None, SNAPSHOTS=None):
        super(IMAGESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, TYPE, DISK_TYPE, PERSISTENT, REGTIME, SOURCE, PATH, FSTYPE, SIZE, STATE, RUNNING_VMS, CLONING_OPS, CLONING_ID, TARGET_SNAPSHOT, DATASTORE_ID, DATASTORE, VMS, CLONES, APP_CLONES, TEMPLATE, SNAPSHOTS, )
supermod.IMAGE.subclass = IMAGESub
# end class IMAGESub


class MARKETPLACEAPP_POOLSub(TemplatedType, supermod.MARKETPLACEAPP_POOL):
    def __init__(self, MARKETPLACEAPP=None):
        super(MARKETPLACEAPP_POOLSub, self).__init__(MARKETPLACEAPP, )
supermod.MARKETPLACEAPP_POOL.subclass = MARKETPLACEAPP_POOLSub
# end class MARKETPLACEAPP_POOLSub


class MARKETPLACEAPPSub(TemplatedType, supermod.MARKETPLACEAPP):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, REGTIME=None, NAME=None, ZONE_ID=None, ORIGIN_ID=None, SOURCE=None, MD5=None, SIZE=None, DESCRIPTION=None, VERSION=None, FORMAT=None, APPTEMPLATE64=None, MARKETPLACE_ID=None, MARKETPLACE=None, STATE=None, TYPE=None, PERMISSIONS=None, TEMPLATE=None):
        super(MARKETPLACEAPPSub, self).__init__(ID, UID, GID, UNAME, GNAME, REGTIME, NAME, ZONE_ID, ORIGIN_ID, SOURCE, MD5, SIZE, DESCRIPTION, VERSION, FORMAT, APPTEMPLATE64, MARKETPLACE_ID, MARKETPLACE, STATE, TYPE, PERMISSIONS, TEMPLATE, )
supermod.MARKETPLACEAPP.subclass = MARKETPLACEAPPSub
# end class MARKETPLACEAPPSub


class MARKETPLACE_POOLSub(TemplatedType, supermod.MARKETPLACE_POOL):
    def __init__(self, MARKETPLACE=None):
        super(MARKETPLACE_POOLSub, self).__init__(MARKETPLACE, )
supermod.MARKETPLACE_POOL.subclass = MARKETPLACE_POOLSub
# end class MARKETPLACE_POOLSub


class MARKETPLACESub(TemplatedType, supermod.MARKETPLACE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, MARKET_MAD=None, ZONE_ID=None, TOTAL_MB=None, FREE_MB=None, USED_MB=None, MARKETPLACEAPPS=None, PERMISSIONS=None, TEMPLATE=None):
        super(MARKETPLACESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, MARKET_MAD, ZONE_ID, TOTAL_MB, FREE_MB, USED_MB, MARKETPLACEAPPS, PERMISSIONS, TEMPLATE, )
supermod.MARKETPLACE.subclass = MARKETPLACESub
# end class MARKETPLACESub


class USER_POOLSub(TemplatedType, supermod.USER_POOL):
    def __init__(self, USER=None, QUOTAS=None, DEFAULT_USER_QUOTAS=None):
        super(USER_POOLSub, self).__init__(USER, QUOTAS, DEFAULT_USER_QUOTAS, )
supermod.USER_POOL.subclass = USER_POOLSub
# end class USER_POOLSub


class USERSub(TemplatedType, supermod.USER):
    def __init__(self, ID=None, GID=None, GROUPS=None, GNAME=None, NAME=None, PASSWORD=None, AUTH_DRIVER=None, ENABLED=None, LOGIN_TOKEN=None, TEMPLATE=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, DEFAULT_USER_QUOTAS=None):
        super(USERSub, self).__init__(ID, GID, GROUPS, GNAME, NAME, PASSWORD, AUTH_DRIVER, ENABLED, LOGIN_TOKEN, TEMPLATE, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, DEFAULT_USER_QUOTAS, )
supermod.USER.subclass = USERSub
# end class USERSub


class VDC_POOLSub(TemplatedType, supermod.VDC_POOL):
    def __init__(self, VDC=None):
        super(VDC_POOLSub, self).__init__(VDC, )
supermod.VDC_POOL.subclass = VDC_POOLSub
# end class VDC_POOLSub


class VDCSub(TemplatedType, supermod.VDC):
    def __init__(self, ID=None, NAME=None, GROUPS=None, CLUSTERS=None, HOSTS=None, DATASTORES=None, VNETS=None, TEMPLATE=None):
        super(VDCSub, self).__init__(ID, NAME, GROUPS, CLUSTERS, HOSTS, DATASTORES, VNETS, TEMPLATE, )
supermod.VDC.subclass = VDCSub
# end class VDCSub


class VM_POOLSub(TemplatedType, supermod.VM_POOL):
    def __init__(self, VM=None):
        super(VM_POOLSub, self).__init__(VM, )
supermod.VM_POOL.subclass = VM_POOLSub
# end class VM_POOLSub


class VMSub(TemplatedType, supermod.VM):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, LAST_POLL=None, STATE=None, LCM_STATE=None, PREV_STATE=None, PREV_LCM_STATE=None, RESCHED=None, STIME=None, ETIME=None, DEPLOY_ID=None, MONITORING=None, TEMPLATE=None, USER_TEMPLATE=None, HISTORY_RECORDS=None, SNAPSHOTS=None):
        super(VMSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, LAST_POLL, STATE, LCM_STATE, PREV_STATE, PREV_LCM_STATE, RESCHED, STIME, ETIME, DEPLOY_ID, MONITORING, TEMPLATE, USER_TEMPLATE, HISTORY_RECORDS, SNAPSHOTS, )
supermod.VM.subclass = VMSub
# end class VMSub


class VMTEMPLATE_POOLSub(TemplatedType, supermod.VMTEMPLATE_POOL):
    def __init__(self, VMTEMPLATE=None):
        super(VMTEMPLATE_POOLSub, self).__init__(VMTEMPLATE, )
supermod.VMTEMPLATE_POOL.subclass = VMTEMPLATE_POOLSub
# end class VMTEMPLATE_POOLSub


class VMTEMPLATESub(TemplatedType, supermod.VMTEMPLATE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, REGTIME=None, TEMPLATE=None):
        super(VMTEMPLATESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, REGTIME, TEMPLATE, )
supermod.VMTEMPLATE.subclass = VMTEMPLATESub
# end class VMTEMPLATESub


class VNET_POOLSub(TemplatedType, supermod.VNET_POOL):
    def __init__(self, VNET=None):
        super(VNET_POOLSub, self).__init__(VNET, )
supermod.VNET_POOL.subclass = VNET_POOLSub
# end class VNET_POOLSub


class VNETSub(TemplatedType, supermod.VNET):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, CLUSTERS=None, BRIDGE=None, PARENT_NETWORK_ID=None, VN_MAD=None, PHYDEV=None, VLAN_ID=None, VLAN_ID_AUTOMATIC=None, USED_LEASES=None, VROUTERS=None, TEMPLATE=None, AR_POOL=None):
        super(VNETSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, CLUSTERS, BRIDGE, PARENT_NETWORK_ID, VN_MAD, PHYDEV, VLAN_ID, VLAN_ID_AUTOMATIC, USED_LEASES, VROUTERS, TEMPLATE, AR_POOL, )
supermod.VNET.subclass = VNETSub
# end class VNETSub


class VROUTER_POOLSub(TemplatedType, supermod.VROUTER_POOL):
    def __init__(self, VROUTER=None):
        super(VROUTER_POOLSub, self).__init__(VROUTER, )
supermod.VROUTER_POOL.subclass = VROUTER_POOLSub
# end class VROUTER_POOLSub


class VROUTERSub(TemplatedType, supermod.VROUTER):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, VMS=None, TEMPLATE=None):
        super(VROUTERSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, VMS, TEMPLATE, )
supermod.VROUTER.subclass = VROUTERSub
# end class VROUTERSub


class VMTypeSub(TemplatedType, supermod.VMType):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, LAST_POLL=None, STATE=None, LCM_STATE=None, PREV_STATE=None, PREV_LCM_STATE=None, RESCHED=None, STIME=None, ETIME=None, DEPLOY_ID=None, MONITORING=None, TEMPLATE=None, USER_TEMPLATE=None, HISTORY_RECORDS=None, SNAPSHOTS=None):
        super(VMTypeSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, LAST_POLL, STATE, LCM_STATE, PREV_STATE, PREV_LCM_STATE, RESCHED, STIME, ETIME, DEPLOY_ID, MONITORING, TEMPLATE, USER_TEMPLATE, HISTORY_RECORDS, SNAPSHOTS, )
supermod.VMType.subclass = VMTypeSub
# end class VMTypeSub


class PERMISSIONSTypeSub(TemplatedType, supermod.PERMISSIONSType):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None):
        super(PERMISSIONSTypeSub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A, )
supermod.PERMISSIONSType.subclass = PERMISSIONSTypeSub
# end class PERMISSIONSTypeSub


class SNAPSHOTSTypeSub(TemplatedType, supermod.SNAPSHOTSType):
    def __init__(self, DISK_ID=None, SNAPSHOT=None):
        super(SNAPSHOTSTypeSub, self).__init__(DISK_ID, SNAPSHOT, )
supermod.SNAPSHOTSType.subclass = SNAPSHOTSTypeSub
# end class SNAPSHOTSTypeSub


class SNAPSHOTTypeSub(TemplatedType, supermod.SNAPSHOTType):
    def __init__(self, ACTIVE=None, CHILDREN=None, DATE=None, ID=None, NAME=None, PARENT=None, SIZE=None):
        super(SNAPSHOTTypeSub, self).__init__(ACTIVE, CHILDREN, DATE, ID, NAME, PARENT, SIZE, )
supermod.SNAPSHOTType.subclass = SNAPSHOTTypeSub
# end class SNAPSHOTTypeSub


class HOSTSTypeSub(TemplatedType, supermod.HOSTSType):
    def __init__(self, ID=None):
        super(HOSTSTypeSub, self).__init__(ID, )
supermod.HOSTSType.subclass = HOSTSTypeSub
# end class HOSTSTypeSub


class DATASTORESTypeSub(TemplatedType, supermod.DATASTORESType):
    def __init__(self, ID=None):
        super(DATASTORESTypeSub, self).__init__(ID, )
supermod.DATASTORESType.subclass = DATASTORESTypeSub
# end class DATASTORESTypeSub


class VNETSTypeSub(TemplatedType, supermod.VNETSType):
    def __init__(self, ID=None):
        super(VNETSTypeSub, self).__init__(ID, )
supermod.VNETSType.subclass = VNETSTypeSub
# end class VNETSTypeSub


class PERMISSIONSType1Sub(TemplatedType, supermod.PERMISSIONSType1):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None):
        super(PERMISSIONSType1Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A, )
supermod.PERMISSIONSType1.subclass = PERMISSIONSType1Sub
# end class PERMISSIONSType1Sub


class CLUSTERSTypeSub(TemplatedType, supermod.CLUSTERSType):
    def __init__(self, ID=None):
        super(CLUSTERSTypeSub, self).__init__(ID, )
supermod.CLUSTERSType.subclass = CLUSTERSTypeSub
# end class CLUSTERSTypeSub


class IMAGESTypeSub(TemplatedType, supermod.IMAGESType):
    def __init__(self, ID=None):
        super(IMAGESTypeSub, self).__init__(ID, )
supermod.IMAGESType.subclass = IMAGESTypeSub
# end class IMAGESTypeSub


class GROUPTypeSub(TemplatedType, supermod.GROUPType):
    def __init__(self, ID=None, NAME=None, TEMPLATE=None, USERS=None, ADMINS=None):
        super(GROUPTypeSub, self).__init__(ID, NAME, TEMPLATE, USERS, ADMINS, )
supermod.GROUPType.subclass = GROUPTypeSub
# end class GROUPTypeSub


class USERSTypeSub(TemplatedType, supermod.USERSType):
    def __init__(self, ID=None):
        super(USERSTypeSub, self).__init__(ID, )
supermod.USERSType.subclass = USERSTypeSub
# end class USERSTypeSub


class ADMINSTypeSub(TemplatedType, supermod.ADMINSType):
    def __init__(self, ID=None):
        super(ADMINSTypeSub, self).__init__(ID, )
supermod.ADMINSType.subclass = ADMINSTypeSub
# end class ADMINSTypeSub


class QUOTASTypeSub(TemplatedType, supermod.QUOTASType):
    def __init__(self, ID=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None):
        super(QUOTASTypeSub, self).__init__(ID, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, )
supermod.QUOTASType.subclass = QUOTASTypeSub
# end class QUOTASTypeSub


class DATASTORE_QUOTATypeSub(TemplatedType, supermod.DATASTORE_QUOTAType):
    def __init__(self, DATASTORE=None):
        super(DATASTORE_QUOTATypeSub, self).__init__(DATASTORE, )
supermod.DATASTORE_QUOTAType.subclass = DATASTORE_QUOTATypeSub
# end class DATASTORE_QUOTATypeSub


class DATASTORETypeSub(TemplatedType, supermod.DATASTOREType):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None):
        super(DATASTORETypeSub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED, )
supermod.DATASTOREType.subclass = DATASTORETypeSub
# end class DATASTORETypeSub


class NETWORK_QUOTATypeSub(TemplatedType, supermod.NETWORK_QUOTAType):
    def __init__(self, NETWORK=None):
        super(NETWORK_QUOTATypeSub, self).__init__(NETWORK, )
supermod.NETWORK_QUOTAType.subclass = NETWORK_QUOTATypeSub
# end class NETWORK_QUOTATypeSub


class NETWORKTypeSub(TemplatedType, supermod.NETWORKType):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None):
        super(NETWORKTypeSub, self).__init__(ID, LEASES, LEASES_USED, )
supermod.NETWORKType.subclass = NETWORKTypeSub
# end class NETWORKTypeSub


class VM_QUOTATypeSub(TemplatedType, supermod.VM_QUOTAType):
    def __init__(self, VM=None):
        super(VM_QUOTATypeSub, self).__init__(VM, )
supermod.VM_QUOTAType.subclass = VM_QUOTATypeSub
# end class VM_QUOTATypeSub


class VMType2Sub(TemplatedType, supermod.VMType2):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None):
        super(VMType2Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED, )
supermod.VMType2.subclass = VMType2Sub
# end class VMType2Sub


class IMAGE_QUOTATypeSub(TemplatedType, supermod.IMAGE_QUOTAType):
    def __init__(self, IMAGE=None):
        super(IMAGE_QUOTATypeSub, self).__init__(IMAGE, )
supermod.IMAGE_QUOTAType.subclass = IMAGE_QUOTATypeSub
# end class IMAGE_QUOTATypeSub


class IMAGETypeSub(TemplatedType, supermod.IMAGEType):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None):
        super(IMAGETypeSub, self).__init__(ID, RVMS, RVMS_USED, )
supermod.IMAGEType.subclass = IMAGETypeSub
# end class IMAGETypeSub


class DEFAULT_GROUP_QUOTASTypeSub(TemplatedType, supermod.DEFAULT_GROUP_QUOTASType):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None):
        super(DEFAULT_GROUP_QUOTASTypeSub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, )
supermod.DEFAULT_GROUP_QUOTASType.subclass = DEFAULT_GROUP_QUOTASTypeSub
# end class DEFAULT_GROUP_QUOTASTypeSub


class DATASTORE_QUOTAType3Sub(TemplatedType, supermod.DATASTORE_QUOTAType3):
    def __init__(self, DATASTORE=None):
        super(DATASTORE_QUOTAType3Sub, self).__init__(DATASTORE, )
supermod.DATASTORE_QUOTAType3.subclass = DATASTORE_QUOTAType3Sub
# end class DATASTORE_QUOTAType3Sub


class DATASTOREType4Sub(TemplatedType, supermod.DATASTOREType4):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None):
        super(DATASTOREType4Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED, )
supermod.DATASTOREType4.subclass = DATASTOREType4Sub
# end class DATASTOREType4Sub


class NETWORK_QUOTAType5Sub(TemplatedType, supermod.NETWORK_QUOTAType5):
    def __init__(self, NETWORK=None):
        super(NETWORK_QUOTAType5Sub, self).__init__(NETWORK, )
supermod.NETWORK_QUOTAType5.subclass = NETWORK_QUOTAType5Sub
# end class NETWORK_QUOTAType5Sub


class NETWORKType6Sub(TemplatedType, supermod.NETWORKType6):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None):
        super(NETWORKType6Sub, self).__init__(ID, LEASES, LEASES_USED, )
supermod.NETWORKType6.subclass = NETWORKType6Sub
# end class NETWORKType6Sub


class VM_QUOTAType7Sub(TemplatedType, supermod.VM_QUOTAType7):
    def __init__(self, VM=None):
        super(VM_QUOTAType7Sub, self).__init__(VM, )
supermod.VM_QUOTAType7.subclass = VM_QUOTAType7Sub
# end class VM_QUOTAType7Sub


class VMType8Sub(TemplatedType, supermod.VMType8):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None):
        super(VMType8Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED, )
supermod.VMType8.subclass = VMType8Sub
# end class VMType8Sub


class IMAGE_QUOTAType9Sub(TemplatedType, supermod.IMAGE_QUOTAType9):
    def __init__(self, IMAGE=None):
        super(IMAGE_QUOTAType9Sub, self).__init__(IMAGE, )
supermod.IMAGE_QUOTAType9.subclass = IMAGE_QUOTAType9Sub
# end class IMAGE_QUOTAType9Sub


class IMAGEType10Sub(TemplatedType, supermod.IMAGEType10):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None):
        super(IMAGEType10Sub, self).__init__(ID, RVMS, RVMS_USED, )
supermod.IMAGEType10.subclass = IMAGEType10Sub
# end class IMAGEType10Sub


class USERSType11Sub(TemplatedType, supermod.USERSType11):
    def __init__(self, ID=None):
        super(USERSType11Sub, self).__init__(ID, )
supermod.USERSType11.subclass = USERSType11Sub
# end class USERSType11Sub


class ADMINSType12Sub(TemplatedType, supermod.ADMINSType12):
    def __init__(self, ID=None):
        super(ADMINSType12Sub, self).__init__(ID, )
supermod.ADMINSType12.subclass = ADMINSType12Sub
# end class ADMINSType12Sub


class DATASTORE_QUOTAType13Sub(TemplatedType, supermod.DATASTORE_QUOTAType13):
    def __init__(self, DATASTORE=None):
        super(DATASTORE_QUOTAType13Sub, self).__init__(DATASTORE, )
supermod.DATASTORE_QUOTAType13.subclass = DATASTORE_QUOTAType13Sub
# end class DATASTORE_QUOTAType13Sub


class DATASTOREType14Sub(TemplatedType, supermod.DATASTOREType14):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None):
        super(DATASTOREType14Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED, )
supermod.DATASTOREType14.subclass = DATASTOREType14Sub
# end class DATASTOREType14Sub


class NETWORK_QUOTAType15Sub(TemplatedType, supermod.NETWORK_QUOTAType15):
    def __init__(self, NETWORK=None):
        super(NETWORK_QUOTAType15Sub, self).__init__(NETWORK, )
supermod.NETWORK_QUOTAType15.subclass = NETWORK_QUOTAType15Sub
# end class NETWORK_QUOTAType15Sub


class NETWORKType16Sub(TemplatedType, supermod.NETWORKType16):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None):
        super(NETWORKType16Sub, self).__init__(ID, LEASES, LEASES_USED, )
supermod.NETWORKType16.subclass = NETWORKType16Sub
# end class NETWORKType16Sub


class VM_QUOTAType17Sub(TemplatedType, supermod.VM_QUOTAType17):
    def __init__(self, VM=None):
        super(VM_QUOTAType17Sub, self).__init__(VM, )
supermod.VM_QUOTAType17.subclass = VM_QUOTAType17Sub
# end class VM_QUOTAType17Sub


class VMType18Sub(TemplatedType, supermod.VMType18):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None):
        super(VMType18Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED, )
supermod.VMType18.subclass = VMType18Sub
# end class VMType18Sub


class IMAGE_QUOTAType19Sub(TemplatedType, supermod.IMAGE_QUOTAType19):
    def __init__(self, IMAGE=None):
        super(IMAGE_QUOTAType19Sub, self).__init__(IMAGE, )
supermod.IMAGE_QUOTAType19.subclass = IMAGE_QUOTAType19Sub
# end class IMAGE_QUOTAType19Sub


class IMAGEType20Sub(TemplatedType, supermod.IMAGEType20):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None):
        super(IMAGEType20Sub, self).__init__(ID, RVMS, RVMS_USED, )
supermod.IMAGEType20.subclass = IMAGEType20Sub
# end class IMAGEType20Sub


class DEFAULT_GROUP_QUOTASType21Sub(TemplatedType, supermod.DEFAULT_GROUP_QUOTASType21):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None):
        super(DEFAULT_GROUP_QUOTASType21Sub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, )
supermod.DEFAULT_GROUP_QUOTASType21.subclass = DEFAULT_GROUP_QUOTASType21Sub
# end class DEFAULT_GROUP_QUOTASType21Sub


class DATASTORE_QUOTAType22Sub(TemplatedType, supermod.DATASTORE_QUOTAType22):
    def __init__(self, DATASTORE=None):
        super(DATASTORE_QUOTAType22Sub, self).__init__(DATASTORE, )
supermod.DATASTORE_QUOTAType22.subclass = DATASTORE_QUOTAType22Sub
# end class DATASTORE_QUOTAType22Sub


class DATASTOREType23Sub(TemplatedType, supermod.DATASTOREType23):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None):
        super(DATASTOREType23Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED, )
supermod.DATASTOREType23.subclass = DATASTOREType23Sub
# end class DATASTOREType23Sub


class NETWORK_QUOTAType24Sub(TemplatedType, supermod.NETWORK_QUOTAType24):
    def __init__(self, NETWORK=None):
        super(NETWORK_QUOTAType24Sub, self).__init__(NETWORK, )
supermod.NETWORK_QUOTAType24.subclass = NETWORK_QUOTAType24Sub
# end class NETWORK_QUOTAType24Sub


class NETWORKType25Sub(TemplatedType, supermod.NETWORKType25):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None):
        super(NETWORKType25Sub, self).__init__(ID, LEASES, LEASES_USED, )
supermod.NETWORKType25.subclass = NETWORKType25Sub
# end class NETWORKType25Sub


class VM_QUOTAType26Sub(TemplatedType, supermod.VM_QUOTAType26):
    def __init__(self, VM=None):
        super(VM_QUOTAType26Sub, self).__init__(VM, )
supermod.VM_QUOTAType26.subclass = VM_QUOTAType26Sub
# end class VM_QUOTAType26Sub


class VMType27Sub(TemplatedType, supermod.VMType27):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None):
        super(VMType27Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED, )
supermod.VMType27.subclass = VMType27Sub
# end class VMType27Sub


class IMAGE_QUOTAType28Sub(TemplatedType, supermod.IMAGE_QUOTAType28):
    def __init__(self, IMAGE=None):
        super(IMAGE_QUOTAType28Sub, self).__init__(IMAGE, )
supermod.IMAGE_QUOTAType28.subclass = IMAGE_QUOTAType28Sub
# end class IMAGE_QUOTAType28Sub


class IMAGEType29Sub(TemplatedType, supermod.IMAGEType29):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None):
        super(IMAGEType29Sub, self).__init__(ID, RVMS, RVMS_USED, )
supermod.IMAGEType29.subclass = IMAGEType29Sub
# end class IMAGEType29Sub


class HOST_SHARETypeSub(TemplatedType, supermod.HOST_SHAREType):
    def __init__(self, DISK_USAGE=None, MEM_USAGE=None, CPU_USAGE=None, TOTAL_MEM=None, TOTAL_CPU=None, MAX_DISK=None, MAX_MEM=None, MAX_CPU=None, FREE_DISK=None, FREE_MEM=None, FREE_CPU=None, USED_DISK=None, USED_MEM=None, USED_CPU=None, RUNNING_VMS=None, DATASTORES=None, PCI_DEVICES=None):
        super(HOST_SHARETypeSub, self).__init__(DISK_USAGE, MEM_USAGE, CPU_USAGE, TOTAL_MEM, TOTAL_CPU, MAX_DISK, MAX_MEM, MAX_CPU, FREE_DISK, FREE_MEM, FREE_CPU, USED_DISK, USED_MEM, USED_CPU, RUNNING_VMS, DATASTORES, PCI_DEVICES, )
supermod.HOST_SHAREType.subclass = HOST_SHARETypeSub
# end class HOST_SHARETypeSub


class DATASTORESType30Sub(TemplatedType, supermod.DATASTORESType30):
    def __init__(self, DS=None):
        super(DATASTORESType30Sub, self).__init__(DS, )
supermod.DATASTORESType30.subclass = DATASTORESType30Sub
# end class DATASTORESType30Sub


class DSTypeSub(TemplatedType, supermod.DSType):
    def __init__(self, ID=None, FREE_MB=None, TOTAL_MB=None, USED_MB=None):
        super(DSTypeSub, self).__init__(ID, FREE_MB, TOTAL_MB, USED_MB, )
supermod.DSType.subclass = DSTypeSub
# end class DSTypeSub


class PCI_DEVICESTypeSub(TemplatedType, supermod.PCI_DEVICESType):
    def __init__(self, PCI=None):
        super(PCI_DEVICESTypeSub, self).__init__(PCI, )
supermod.PCI_DEVICESType.subclass = PCI_DEVICESTypeSub
# end class PCI_DEVICESTypeSub


class VMSTypeSub(TemplatedType, supermod.VMSType):
    def __init__(self, ID=None):
        super(VMSTypeSub, self).__init__(ID, )
supermod.VMSType.subclass = VMSTypeSub
# end class VMSTypeSub


class PERMISSIONSType31Sub(TemplatedType, supermod.PERMISSIONSType31):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None):
        super(PERMISSIONSType31Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A, )
supermod.PERMISSIONSType31.subclass = PERMISSIONSType31Sub
# end class PERMISSIONSType31Sub


class VMSType32Sub(TemplatedType, supermod.VMSType32):
    def __init__(self, ID=None):
        super(VMSType32Sub, self).__init__(ID, )
supermod.VMSType32.subclass = VMSType32Sub
# end class VMSType32Sub


class CLONESTypeSub(TemplatedType, supermod.CLONESType):
    def __init__(self, ID=None):
        super(CLONESTypeSub, self).__init__(ID, )
supermod.CLONESType.subclass = CLONESTypeSub
# end class CLONESTypeSub


class APP_CLONESTypeSub(TemplatedType, supermod.APP_CLONESType):
    def __init__(self, ID=None):
        super(APP_CLONESTypeSub, self).__init__(ID, )
supermod.APP_CLONESType.subclass = APP_CLONESTypeSub
# end class APP_CLONESTypeSub


class SNAPSHOTSType33Sub(TemplatedType, supermod.SNAPSHOTSType33):
    def __init__(self, ALLOW_ORPHANS=None, SNAPSHOT=None):
        super(SNAPSHOTSType33Sub, self).__init__(ALLOW_ORPHANS, SNAPSHOT, )
supermod.SNAPSHOTSType33.subclass = SNAPSHOTSType33Sub
# end class SNAPSHOTSType33Sub


class SNAPSHOTType34Sub(TemplatedType, supermod.SNAPSHOTType34):
    def __init__(self, CHILDREN=None, ACTIVE=None, DATE=None, ID=None, NAME=None, PARENT=None, SIZE=None):
        super(SNAPSHOTType34Sub, self).__init__(CHILDREN, ACTIVE, DATE, ID, NAME, PARENT, SIZE, )
supermod.SNAPSHOTType34.subclass = SNAPSHOTType34Sub
# end class SNAPSHOTType34Sub


class PERMISSIONSType35Sub(TemplatedType, supermod.PERMISSIONSType35):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None):
        super(PERMISSIONSType35Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A, )
supermod.PERMISSIONSType35.subclass = PERMISSIONSType35Sub
# end class PERMISSIONSType35Sub


class MARKETPLACEAPPSTypeSub(TemplatedType, supermod.MARKETPLACEAPPSType):
    def __init__(self, ID=None):
        super(MARKETPLACEAPPSTypeSub, self).__init__(ID, )
supermod.MARKETPLACEAPPSType.subclass = MARKETPLACEAPPSTypeSub
# end class MARKETPLACEAPPSTypeSub


class PERMISSIONSType36Sub(TemplatedType, supermod.PERMISSIONSType36):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None):
        super(PERMISSIONSType36Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A, )
supermod.PERMISSIONSType36.subclass = PERMISSIONSType36Sub
# end class PERMISSIONSType36Sub


class USERTypeSub(TemplatedType, supermod.USERType):
    def __init__(self, ID=None, GID=None, GROUPS=None, GNAME=None, NAME=None, PASSWORD=None, AUTH_DRIVER=None, ENABLED=None, LOGIN_TOKEN=None, TEMPLATE=None):
        super(USERTypeSub, self).__init__(ID, GID, GROUPS, GNAME, NAME, PASSWORD, AUTH_DRIVER, ENABLED, LOGIN_TOKEN, TEMPLATE, )
supermod.USERType.subclass = USERTypeSub
# end class USERTypeSub


class GROUPSTypeSub(TemplatedType, supermod.GROUPSType):
    def __init__(self, ID=None):
        super(GROUPSTypeSub, self).__init__(ID, )
supermod.GROUPSType.subclass = GROUPSTypeSub
# end class GROUPSTypeSub


class LOGIN_TOKENTypeSub(TemplatedType, supermod.LOGIN_TOKENType):
    def __init__(self, TOKEN=None, EXPIRATION_TIME=None, EGID=None):
        super(LOGIN_TOKENTypeSub, self).__init__(TOKEN, EXPIRATION_TIME, EGID, )
supermod.LOGIN_TOKENType.subclass = LOGIN_TOKENTypeSub
# end class LOGIN_TOKENTypeSub


class QUOTASType37Sub(TemplatedType, supermod.QUOTASType37):
    def __init__(self, ID=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None):
        super(QUOTASType37Sub, self).__init__(ID, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, )
supermod.QUOTASType37.subclass = QUOTASType37Sub
# end class QUOTASType37Sub


class DATASTORE_QUOTAType38Sub(TemplatedType, supermod.DATASTORE_QUOTAType38):
    def __init__(self, DATASTORE=None):
        super(DATASTORE_QUOTAType38Sub, self).__init__(DATASTORE, )
supermod.DATASTORE_QUOTAType38.subclass = DATASTORE_QUOTAType38Sub
# end class DATASTORE_QUOTAType38Sub


class DATASTOREType39Sub(TemplatedType, supermod.DATASTOREType39):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None):
        super(DATASTOREType39Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED, )
supermod.DATASTOREType39.subclass = DATASTOREType39Sub
# end class DATASTOREType39Sub


class NETWORK_QUOTAType40Sub(TemplatedType, supermod.NETWORK_QUOTAType40):
    def __init__(self, NETWORK=None):
        super(NETWORK_QUOTAType40Sub, self).__init__(NETWORK, )
supermod.NETWORK_QUOTAType40.subclass = NETWORK_QUOTAType40Sub
# end class NETWORK_QUOTAType40Sub


class NETWORKType41Sub(TemplatedType, supermod.NETWORKType41):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None):
        super(NETWORKType41Sub, self).__init__(ID, LEASES, LEASES_USED, )
supermod.NETWORKType41.subclass = NETWORKType41Sub
# end class NETWORKType41Sub


class VM_QUOTAType42Sub(TemplatedType, supermod.VM_QUOTAType42):
    def __init__(self, VM=None):
        super(VM_QUOTAType42Sub, self).__init__(VM, )
supermod.VM_QUOTAType42.subclass = VM_QUOTAType42Sub
# end class VM_QUOTAType42Sub


class VMType43Sub(TemplatedType, supermod.VMType43):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None):
        super(VMType43Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED, )
supermod.VMType43.subclass = VMType43Sub
# end class VMType43Sub


class IMAGE_QUOTAType44Sub(TemplatedType, supermod.IMAGE_QUOTAType44):
    def __init__(self, IMAGE=None):
        super(IMAGE_QUOTAType44Sub, self).__init__(IMAGE, )
supermod.IMAGE_QUOTAType44.subclass = IMAGE_QUOTAType44Sub
# end class IMAGE_QUOTAType44Sub


class IMAGEType45Sub(TemplatedType, supermod.IMAGEType45):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None):
        super(IMAGEType45Sub, self).__init__(ID, RVMS, RVMS_USED, )
supermod.IMAGEType45.subclass = IMAGEType45Sub
# end class IMAGEType45Sub


class DEFAULT_USER_QUOTASTypeSub(TemplatedType, supermod.DEFAULT_USER_QUOTASType):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None):
        super(DEFAULT_USER_QUOTASTypeSub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, )
supermod.DEFAULT_USER_QUOTASType.subclass = DEFAULT_USER_QUOTASTypeSub
# end class DEFAULT_USER_QUOTASTypeSub


class DATASTORE_QUOTAType46Sub(TemplatedType, supermod.DATASTORE_QUOTAType46):
    def __init__(self, DATASTORE=None):
        super(DATASTORE_QUOTAType46Sub, self).__init__(DATASTORE, )
supermod.DATASTORE_QUOTAType46.subclass = DATASTORE_QUOTAType46Sub
# end class DATASTORE_QUOTAType46Sub


class DATASTOREType47Sub(TemplatedType, supermod.DATASTOREType47):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None):
        super(DATASTOREType47Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED, )
supermod.DATASTOREType47.subclass = DATASTOREType47Sub
# end class DATASTOREType47Sub


class NETWORK_QUOTAType48Sub(TemplatedType, supermod.NETWORK_QUOTAType48):
    def __init__(self, NETWORK=None):
        super(NETWORK_QUOTAType48Sub, self).__init__(NETWORK, )
supermod.NETWORK_QUOTAType48.subclass = NETWORK_QUOTAType48Sub
# end class NETWORK_QUOTAType48Sub


class NETWORKType49Sub(TemplatedType, supermod.NETWORKType49):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None):
        super(NETWORKType49Sub, self).__init__(ID, LEASES, LEASES_USED, )
supermod.NETWORKType49.subclass = NETWORKType49Sub
# end class NETWORKType49Sub


class VM_QUOTAType50Sub(TemplatedType, supermod.VM_QUOTAType50):
    def __init__(self, VM=None):
        super(VM_QUOTAType50Sub, self).__init__(VM, )
supermod.VM_QUOTAType50.subclass = VM_QUOTAType50Sub
# end class VM_QUOTAType50Sub


class VMType51Sub(TemplatedType, supermod.VMType51):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None):
        super(VMType51Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED, )
supermod.VMType51.subclass = VMType51Sub
# end class VMType51Sub


class IMAGE_QUOTAType52Sub(TemplatedType, supermod.IMAGE_QUOTAType52):
    def __init__(self, IMAGE=None):
        super(IMAGE_QUOTAType52Sub, self).__init__(IMAGE, )
supermod.IMAGE_QUOTAType52.subclass = IMAGE_QUOTAType52Sub
# end class IMAGE_QUOTAType52Sub


class IMAGEType53Sub(TemplatedType, supermod.IMAGEType53):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None):
        super(IMAGEType53Sub, self).__init__(ID, RVMS, RVMS_USED, )
supermod.IMAGEType53.subclass = IMAGEType53Sub
# end class IMAGEType53Sub


class GROUPSType54Sub(TemplatedType, supermod.GROUPSType54):
    def __init__(self, ID=None):
        super(GROUPSType54Sub, self).__init__(ID, )
supermod.GROUPSType54.subclass = GROUPSType54Sub
# end class GROUPSType54Sub


class LOGIN_TOKENType55Sub(TemplatedType, supermod.LOGIN_TOKENType55):
    def __init__(self, TOKEN=None, EXPIRATION_TIME=None, EGID=None):
        super(LOGIN_TOKENType55Sub, self).__init__(TOKEN, EXPIRATION_TIME, EGID, )
supermod.LOGIN_TOKENType55.subclass = LOGIN_TOKENType55Sub
# end class LOGIN_TOKENType55Sub


class DATASTORE_QUOTAType56Sub(TemplatedType, supermod.DATASTORE_QUOTAType56):
    def __init__(self, DATASTORE=None):
        super(DATASTORE_QUOTAType56Sub, self).__init__(DATASTORE, )
supermod.DATASTORE_QUOTAType56.subclass = DATASTORE_QUOTAType56Sub
# end class DATASTORE_QUOTAType56Sub


class DATASTOREType57Sub(TemplatedType, supermod.DATASTOREType57):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None):
        super(DATASTOREType57Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED, )
supermod.DATASTOREType57.subclass = DATASTOREType57Sub
# end class DATASTOREType57Sub


class NETWORK_QUOTAType58Sub(TemplatedType, supermod.NETWORK_QUOTAType58):
    def __init__(self, NETWORK=None):
        super(NETWORK_QUOTAType58Sub, self).__init__(NETWORK, )
supermod.NETWORK_QUOTAType58.subclass = NETWORK_QUOTAType58Sub
# end class NETWORK_QUOTAType58Sub


class NETWORKType59Sub(TemplatedType, supermod.NETWORKType59):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None):
        super(NETWORKType59Sub, self).__init__(ID, LEASES, LEASES_USED, )
supermod.NETWORKType59.subclass = NETWORKType59Sub
# end class NETWORKType59Sub


class VM_QUOTAType60Sub(TemplatedType, supermod.VM_QUOTAType60):
    def __init__(self, VM=None):
        super(VM_QUOTAType60Sub, self).__init__(VM, )
supermod.VM_QUOTAType60.subclass = VM_QUOTAType60Sub
# end class VM_QUOTAType60Sub


class VMType61Sub(TemplatedType, supermod.VMType61):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None):
        super(VMType61Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED, )
supermod.VMType61.subclass = VMType61Sub
# end class VMType61Sub


class IMAGE_QUOTAType62Sub(TemplatedType, supermod.IMAGE_QUOTAType62):
    def __init__(self, IMAGE=None):
        super(IMAGE_QUOTAType62Sub, self).__init__(IMAGE, )
supermod.IMAGE_QUOTAType62.subclass = IMAGE_QUOTAType62Sub
# end class IMAGE_QUOTAType62Sub


class IMAGEType63Sub(TemplatedType, supermod.IMAGEType63):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None):
        super(IMAGEType63Sub, self).__init__(ID, RVMS, RVMS_USED, )
supermod.IMAGEType63.subclass = IMAGEType63Sub
# end class IMAGEType63Sub


class DEFAULT_USER_QUOTASType64Sub(TemplatedType, supermod.DEFAULT_USER_QUOTASType64):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None):
        super(DEFAULT_USER_QUOTASType64Sub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, )
supermod.DEFAULT_USER_QUOTASType64.subclass = DEFAULT_USER_QUOTASType64Sub
# end class DEFAULT_USER_QUOTASType64Sub


class DATASTORE_QUOTAType65Sub(TemplatedType, supermod.DATASTORE_QUOTAType65):
    def __init__(self, DATASTORE=None):
        super(DATASTORE_QUOTAType65Sub, self).__init__(DATASTORE, )
supermod.DATASTORE_QUOTAType65.subclass = DATASTORE_QUOTAType65Sub
# end class DATASTORE_QUOTAType65Sub


class DATASTOREType66Sub(TemplatedType, supermod.DATASTOREType66):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None):
        super(DATASTOREType66Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED, )
supermod.DATASTOREType66.subclass = DATASTOREType66Sub
# end class DATASTOREType66Sub


class NETWORK_QUOTAType67Sub(TemplatedType, supermod.NETWORK_QUOTAType67):
    def __init__(self, NETWORK=None):
        super(NETWORK_QUOTAType67Sub, self).__init__(NETWORK, )
supermod.NETWORK_QUOTAType67.subclass = NETWORK_QUOTAType67Sub
# end class NETWORK_QUOTAType67Sub


class NETWORKType68Sub(TemplatedType, supermod.NETWORKType68):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None):
        super(NETWORKType68Sub, self).__init__(ID, LEASES, LEASES_USED, )
supermod.NETWORKType68.subclass = NETWORKType68Sub
# end class NETWORKType68Sub


class VM_QUOTAType69Sub(TemplatedType, supermod.VM_QUOTAType69):
    def __init__(self, VM=None):
        super(VM_QUOTAType69Sub, self).__init__(VM, )
supermod.VM_QUOTAType69.subclass = VM_QUOTAType69Sub
# end class VM_QUOTAType69Sub


class VMType70Sub(TemplatedType, supermod.VMType70):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None):
        super(VMType70Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED, )
supermod.VMType70.subclass = VMType70Sub
# end class VMType70Sub


class IMAGE_QUOTAType71Sub(TemplatedType, supermod.IMAGE_QUOTAType71):
    def __init__(self, IMAGE=None):
        super(IMAGE_QUOTAType71Sub, self).__init__(IMAGE, )
supermod.IMAGE_QUOTAType71.subclass = IMAGE_QUOTAType71Sub
# end class IMAGE_QUOTAType71Sub


class IMAGEType72Sub(TemplatedType, supermod.IMAGEType72):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None):
        super(IMAGEType72Sub, self).__init__(ID, RVMS, RVMS_USED, )
supermod.IMAGEType72.subclass = IMAGEType72Sub
# end class IMAGEType72Sub


class GROUPSType73Sub(TemplatedType, supermod.GROUPSType73):
    def __init__(self, ID=None):
        super(GROUPSType73Sub, self).__init__(ID, )
supermod.GROUPSType73.subclass = GROUPSType73Sub
# end class GROUPSType73Sub


class CLUSTERSType74Sub(TemplatedType, supermod.CLUSTERSType74):
    def __init__(self, CLUSTER=None):
        super(CLUSTERSType74Sub, self).__init__(CLUSTER, )
supermod.CLUSTERSType74.subclass = CLUSTERSType74Sub
# end class CLUSTERSType74Sub


class CLUSTERTypeSub(TemplatedType, supermod.CLUSTERType):
    def __init__(self, ZONE_ID=None, CLUSTER_ID=None):
        super(CLUSTERTypeSub, self).__init__(ZONE_ID, CLUSTER_ID, )
supermod.CLUSTERType.subclass = CLUSTERTypeSub
# end class CLUSTERTypeSub


class HOSTSType75Sub(TemplatedType, supermod.HOSTSType75):
    def __init__(self, HOST=None):
        super(HOSTSType75Sub, self).__init__(HOST, )
supermod.HOSTSType75.subclass = HOSTSType75Sub
# end class HOSTSType75Sub


class HOSTTypeSub(TemplatedType, supermod.HOSTType):
    def __init__(self, ZONE_ID=None, HOST_ID=None):
        super(HOSTTypeSub, self).__init__(ZONE_ID, HOST_ID, )
supermod.HOSTType.subclass = HOSTTypeSub
# end class HOSTTypeSub


class DATASTORESType76Sub(TemplatedType, supermod.DATASTORESType76):
    def __init__(self, DATASTORE=None):
        super(DATASTORESType76Sub, self).__init__(DATASTORE, )
supermod.DATASTORESType76.subclass = DATASTORESType76Sub
# end class DATASTORESType76Sub


class DATASTOREType77Sub(TemplatedType, supermod.DATASTOREType77):
    def __init__(self, ZONE_ID=None, DATASTORE_ID=None):
        super(DATASTOREType77Sub, self).__init__(ZONE_ID, DATASTORE_ID, )
supermod.DATASTOREType77.subclass = DATASTOREType77Sub
# end class DATASTOREType77Sub


class VNETSType78Sub(TemplatedType, supermod.VNETSType78):
    def __init__(self, VNET=None):
        super(VNETSType78Sub, self).__init__(VNET, )
supermod.VNETSType78.subclass = VNETSType78Sub
# end class VNETSType78Sub


class VNETTypeSub(TemplatedType, supermod.VNETType):
    def __init__(self, ZONE_ID=None, VNET_ID=None):
        super(VNETTypeSub, self).__init__(ZONE_ID, VNET_ID, )
supermod.VNETType.subclass = VNETTypeSub
# end class VNETTypeSub


class PERMISSIONSType79Sub(TemplatedType, supermod.PERMISSIONSType79):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None):
        super(PERMISSIONSType79Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A, )
supermod.PERMISSIONSType79.subclass = PERMISSIONSType79Sub
# end class PERMISSIONSType79Sub


class HISTORY_RECORDSTypeSub(TemplatedType, supermod.HISTORY_RECORDSType):
    def __init__(self, HISTORY=None):
        super(HISTORY_RECORDSTypeSub, self).__init__(HISTORY, )
supermod.HISTORY_RECORDSType.subclass = HISTORY_RECORDSTypeSub
# end class HISTORY_RECORDSTypeSub


class HISTORYTypeSub(TemplatedType, supermod.HISTORYType):
    def __init__(self, OID=None, SEQ=None, HOSTNAME=None, HID=None, CID=None, STIME=None, ETIME=None, VM_MAD=None, TM_MAD=None, DS_ID=None, PSTIME=None, PETIME=None, RSTIME=None, RETIME=None, ESTIME=None, EETIME=None, ACTION=None, UID=None, GID=None, REQUEST_ID=None):
        super(HISTORYTypeSub, self).__init__(OID, SEQ, HOSTNAME, HID, CID, STIME, ETIME, VM_MAD, TM_MAD, DS_ID, PSTIME, PETIME, RSTIME, RETIME, ESTIME, EETIME, ACTION, UID, GID, REQUEST_ID, )
supermod.HISTORYType.subclass = HISTORYTypeSub
# end class HISTORYTypeSub


class SNAPSHOTSType80Sub(TemplatedType, supermod.SNAPSHOTSType80):
    def __init__(self, DISK_ID=None, SNAPSHOT=None):
        super(SNAPSHOTSType80Sub, self).__init__(DISK_ID, SNAPSHOT, )
supermod.SNAPSHOTSType80.subclass = SNAPSHOTSType80Sub
# end class SNAPSHOTSType80Sub


class SNAPSHOTType81Sub(TemplatedType, supermod.SNAPSHOTType81):
    def __init__(self, ACTIVE=None, CHILDREN=None, DATE=None, ID=None, NAME=None, PARENT=None, SIZE=None):
        super(SNAPSHOTType81Sub, self).__init__(ACTIVE, CHILDREN, DATE, ID, NAME, PARENT, SIZE, )
supermod.SNAPSHOTType81.subclass = SNAPSHOTType81Sub
# end class SNAPSHOTType81Sub


class PERMISSIONSType82Sub(TemplatedType, supermod.PERMISSIONSType82):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None):
        super(PERMISSIONSType82Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A, )
supermod.PERMISSIONSType82.subclass = PERMISSIONSType82Sub
# end class PERMISSIONSType82Sub


class VNETType83Sub(TemplatedType, supermod.VNETType83):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, CLUSTERS=None, BRIDGE=None, PARENT_NETWORK_ID=None, VN_MAD=None, PHYDEV=None, VLAN_ID=None, VLAN_ID_AUTOMATIC=None, USED_LEASES=None, VROUTERS=None, TEMPLATE=None, AR_POOL=None):
        super(VNETType83Sub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, CLUSTERS, BRIDGE, PARENT_NETWORK_ID, VN_MAD, PHYDEV, VLAN_ID, VLAN_ID_AUTOMATIC, USED_LEASES, VROUTERS, TEMPLATE, AR_POOL, )
supermod.VNETType83.subclass = VNETType83Sub
# end class VNETType83Sub


class PERMISSIONSType84Sub(TemplatedType, supermod.PERMISSIONSType84):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None):
        super(PERMISSIONSType84Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A, )
supermod.PERMISSIONSType84.subclass = PERMISSIONSType84Sub
# end class PERMISSIONSType84Sub


class CLUSTERSType85Sub(TemplatedType, supermod.CLUSTERSType85):
    def __init__(self, ID=None):
        super(CLUSTERSType85Sub, self).__init__(ID, )
supermod.CLUSTERSType85.subclass = CLUSTERSType85Sub
# end class CLUSTERSType85Sub


class VROUTERSTypeSub(TemplatedType, supermod.VROUTERSType):
    def __init__(self, ID=None):
        super(VROUTERSTypeSub, self).__init__(ID, )
supermod.VROUTERSType.subclass = VROUTERSTypeSub
# end class VROUTERSTypeSub


class AR_POOLTypeSub(TemplatedType, supermod.AR_POOLType):
    def __init__(self, AR=None):
        super(AR_POOLTypeSub, self).__init__(AR, )
supermod.AR_POOLType.subclass = AR_POOLTypeSub
# end class AR_POOLTypeSub


class ARTypeSub(TemplatedType, supermod.ARType):
    def __init__(self, ALLOCATED=None, AR_ID=None, GLOBAL_PREFIX=None, IP=None, MAC=None, PARENT_NETWORK_AR_ID=None, SIZE=None, TYPE=None, ULA_PREFIX=None, VN_MAD=None):
        super(ARTypeSub, self).__init__(ALLOCATED, AR_ID, GLOBAL_PREFIX, IP, MAC, PARENT_NETWORK_AR_ID, SIZE, TYPE, ULA_PREFIX, VN_MAD, )
supermod.ARType.subclass = ARTypeSub
# end class ARTypeSub


class PERMISSIONSType86Sub(TemplatedType, supermod.PERMISSIONSType86):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None):
        super(PERMISSIONSType86Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A, )
supermod.PERMISSIONSType86.subclass = PERMISSIONSType86Sub
# end class PERMISSIONSType86Sub


class CLUSTERSType87Sub(TemplatedType, supermod.CLUSTERSType87):
    def __init__(self, ID=None):
        super(CLUSTERSType87Sub, self).__init__(ID, )
supermod.CLUSTERSType87.subclass = CLUSTERSType87Sub
# end class CLUSTERSType87Sub


class VROUTERSType88Sub(TemplatedType, supermod.VROUTERSType88):
    def __init__(self, ID=None):
        super(VROUTERSType88Sub, self).__init__(ID, )
supermod.VROUTERSType88.subclass = VROUTERSType88Sub
# end class VROUTERSType88Sub


class AR_POOLType89Sub(TemplatedType, supermod.AR_POOLType89):
    def __init__(self, AR=None):
        super(AR_POOLType89Sub, self).__init__(AR, )
supermod.AR_POOLType89.subclass = AR_POOLType89Sub
# end class AR_POOLType89Sub


class ARType90Sub(TemplatedType, supermod.ARType90):
    def __init__(self, AR_ID=None, GLOBAL_PREFIX=None, IP=None, MAC=None, PARENT_NETWORK_AR_ID=None, SIZE=None, TYPE=None, ULA_PREFIX=None, VN_MAD=None, MAC_END=None, IP_END=None, IP6_ULA=None, IP6_ULA_END=None, IP6_GLOBAL=None, IP6_GLOBAL_END=None, IP6=None, IP6_END=None, USED_LEASES=None, LEASES=None):
        super(ARType90Sub, self).__init__(AR_ID, GLOBAL_PREFIX, IP, MAC, PARENT_NETWORK_AR_ID, SIZE, TYPE, ULA_PREFIX, VN_MAD, MAC_END, IP_END, IP6_ULA, IP6_ULA_END, IP6_GLOBAL, IP6_GLOBAL_END, IP6, IP6_END, USED_LEASES, LEASES, )
supermod.ARType90.subclass = ARType90Sub
# end class ARType90Sub


class LEASESTypeSub(TemplatedType, supermod.LEASESType):
    def __init__(self, LEASE=None):
        super(LEASESTypeSub, self).__init__(LEASE, )
supermod.LEASESType.subclass = LEASESTypeSub
# end class LEASESTypeSub


class LEASETypeSub(TemplatedType, supermod.LEASEType):
    def __init__(self, IP=None, IP6=None, IP6_GLOBAL=None, IP6_LINK=None, IP6_ULA=None, MAC=None, VM=None, VNET=None, VROUTER=None):
        super(LEASETypeSub, self).__init__(IP, IP6, IP6_GLOBAL, IP6_LINK, IP6_ULA, MAC, VM, VNET, VROUTER, )
supermod.LEASEType.subclass = LEASETypeSub
# end class LEASETypeSub


class PERMISSIONSType91Sub(TemplatedType, supermod.PERMISSIONSType91):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None):
        super(PERMISSIONSType91Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A, )
supermod.PERMISSIONSType91.subclass = PERMISSIONSType91Sub
# end class PERMISSIONSType91Sub


class VMSType92Sub(TemplatedType, supermod.VMSType92):
    def __init__(self, ID=None):
        super(VMSType92Sub, self).__init__(ID, )
supermod.VMSType92.subclass = VMSType92Sub
# end class VMSType92Sub


def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    rootClass = supermod.GDSClassesMapping.get(tag)
    if rootClass is None and hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     if not silence:
##         sys.stdout.write('<?xml version="1.0" ?>\n')
##         rootObj.export(
##             sys.stdout, 0, name_=rootTag,
##             namespacedef_='',
##             pretty_print=True)
    return rootObj


def parseEtree(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    mapping = {}
    rootElement = rootObj.to_etree(None, name_=rootTag, mapping_=mapping)
    reverse_mapping = rootObj.gds_reverse_node_mapping(mapping)
##     if not silence:
##         content = etree_.tostring(
##             rootElement, pretty_print=True,
##             xml_declaration=True, encoding="utf-8")
##         sys.stdout.write(content)
##         sys.stdout.write('\n')
    return rootObj, rootElement, mapping, reverse_mapping


def parseString(inString, silence=False):
    if sys.version_info.major == 2:
        from StringIO import StringIO
    else:
        from io import BytesIO as StringIO
    parser = None
    doc = parsexml_(StringIO(inString), parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     if not silence:
##         sys.stdout.write('<?xml version="1.0" ?>\n')
##         rootObj.export(
##             sys.stdout, 0, name_=rootTag,
##             namespacedef_='')
    return rootObj


def parseLiteral(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     if not silence:
##         sys.stdout.write('#from supbind import *\n\n')
##         sys.stdout.write('from . import supbind as model_\n\n')
##         sys.stdout.write('rootObj = model_.rootClass(\n')
##         rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
##         sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()
