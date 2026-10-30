using System;
using System.Data.SqlClient;
using System.Runtime.Serialization.Formatters.Binary;
using System.IO;
using System.Threading.Tasks;

namespace EnterpriseApp
{
    public class AccountService
    {
        private string apiKey = "auth_token_csharp_987654321";

        public void GetAccount(string userInput)
        {
            string sql = "SELECT * FROM Accounts WHERE Name = '" + userInput + "'";
            using (var cmd = new SqlCommand(sql))
            {
                Console.WriteLine("Executing SQL");
            }
        }

        public object DeserializeUntrusted(Stream stream)
        {
            var formatter = new BinaryFormatter();
            return formatter.Deserialize(stream);
        }

        public void CallAsyncDeadlock(Task<string> worker)
        {
            try
            {
                var result = worker.Result;
            }
            catch
            {
            }
        }
    }
}
