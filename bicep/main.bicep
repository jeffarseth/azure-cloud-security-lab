// Jeffar - main.bicep
// Description -  Bicep template for deploying a basic Azure Virtual Network with public and private subnets,
//                and associated Network Security Groups.
// Created - 2026-07-21
// Last updated - 2026-07-21

@allowed([
  'northcentralus'
  'eastus2'
  'centralus'
  'southcentralus'
  'mexicocentral'
])
@description('Azure region. Restricted to subscription-allowed regions.')
param location string = 'northcentralus'

// map each supported region to its naming suffix, so names never desync from location
var suffixMap = {
  northcentralus: 'ncus'
  eastus2: 'eus2'
  centralus: 'cus'
  southcentralus: 'scus'
  mexicocentral: 'mxc'
}
var regionSuffix = suffixMap[location]

resource nsgPublic 'Microsoft.Network/networkSecurityGroups@2026-01-01' = {
  name: 'nsg-azseclab-public-${regionSuffix}'
  location: location
  properties: {
    securityRules: []
  }
}

resource nsgPrivate 'Microsoft.Network/networkSecurityGroups@2026-01-01' = {
  name: 'nsg-azseclab-private-${regionSuffix}'
  location: location
  properties: {
    securityRules: []
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2026-01-01' = {
  name: 'vnet-azseclab-${regionSuffix}'
  location: location
  properties:{
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
  }
}

resource snetPublic 'Microsoft.Network/virtualNetworks/subnets@2026-01-01' = {
  parent: vnet
  name: 'snet-public'
  properties: {
    addressPrefix: '10.0.0.0/24'
    defaultOutboundAccess: true   // outbound open for apt updates; see networking.md. Prod would use NAT gateway.
    networkSecurityGroup: {
      id: nsgPublic.id
    }
  }
}

resource snetPrivate 'Microsoft.Network/virtualNetworks/subnets@2026-01-01' = {
  parent: vnet
  name: 'snet-private'
  properties: {
    addressPrefix: '10.0.1.0/24'
    defaultOutboundAccess: true   // outbound open for apt updates; see networking.md. Prod would use NAT gateway.
    networkSecurityGroup: {
      id: nsgPrivate.id
    }
  }
}
