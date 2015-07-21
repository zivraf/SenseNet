using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.ServiceBus.Messaging;
using System.Diagnostics;
using System.Threading.Tasks;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Blob;
using Microsoft.WindowsAzure;


namespace EventHubRecv
{
    class Program
    {
        static void Main(string[] args)
        {
            // string eventHubConnectionString = "Endpoint=sb://sensnet-ns.servicebus.windows.net/;SharedAccessKeyName=receiver;SharedAccessKey=nKDaV5RlOrWBSO325P/1LU9qH3znVm+K30nF+dEsnB0=";
            // string eventHubName = "motiontracker";
            string eventHubConnectionString = "Endpoint=sb://sensnet-ns.servicebus.windows.net/;SharedAccessKeyName=manager;SharedAccessKey=ud0mrmEm+jTmQpVqI5EPNxQyfhuTBlspl7lvLmoLXoM=";
            string eventHubName = "discovery";
            string storageAccountName = "sensenet";
            string storageAccountKey = "iSsBgDqpkWeLhGZLWF1LZ21qUUeEeGUxHk1wS84wZ80hxujvPGNMhGxm+MdoL6HTKdTeTjAJrSEiBI1MzrOtaw==";
            string storageConnectionString = string.Format("DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1}",
                storageAccountName, storageAccountKey);

            CloudStorageAccount storageAccount = CreateStorageAccountFromConnectionString(CloudConfigurationManager.GetSetting("StorageConnectionString"));

            // Create a blob client for interacting with the blob service.
            CloudBlobClient blobClient = storageAccount.CreateCloudBlobClient();

            Console.WriteLine("1. Creating Container");
            CloudBlobContainer container = blobClient.GetContainerReference("motiontracker");
            try
            {
                container.CreateIfNotExists();
            }
            catch (StorageException)
            {
                Console.WriteLine("If you are running with the default configuration please make sure you have started the storage emulator. Press the Windows key and type Azure Storage to select and run it from the list of applications - then restart the sample.");
                Console.ReadLine();
                throw;
            }

            string eventProcessorHostName = Guid.NewGuid().ToString();
            EventProcessorHost eventProcessorHost = new EventProcessorHost(eventProcessorHostName, eventHubName, EventHubConsumerGroup.DefaultGroupName, eventHubConnectionString, storageConnectionString);
            Console.WriteLine("Registering EventProcessor...");
            eventProcessorHost.RegisterEventProcessorAsync<SimpleEventProcessor>().Wait();

            Console.WriteLine("Receiving. Press enter key to stop worker.");
            Console.ReadLine();
            eventProcessorHost.UnregisterEventProcessorAsync().Wait();
        }
        private static CloudStorageAccount CreateStorageAccountFromConnectionString(string storageConnectionString)
        {
            CloudStorageAccount storageAccount;
            try
            {
                storageAccount = CloudStorageAccount.Parse(storageConnectionString);
            }
            catch (FormatException)
            {
                Console.WriteLine("Invalid storage account information provided. Please confirm the AccountName and AccountKey are valid in the app.config file - then restart the sample.");
                Console.ReadLine();
                throw;
            }
            catch (ArgumentException)
            {
                Console.WriteLine("Invalid storage account information provided. Please confirm the AccountName and AccountKey are valid in the app.config file - then restart the sample.");
                Console.ReadLine();
                throw;
            }

            return storageAccount;
        }
    }
}
