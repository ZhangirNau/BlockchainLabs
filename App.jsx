import React, { useEffect, useState } from "react";
import { ethers } from "ethers";

//  Контракт адрес
const contractAddress = "0xFAceBF5B8cC6576a118343df333b254D4cb16637";

//  ABI 
const contractABI = [
  {
    inputs: [
      { internalType: "uint256", name: "_maxPrize", type: "uint256" },
      { internalType: "uint256", name: "_hiddenNumber", type: "uint256" },
    ],
    stateMutability: "payable",
    type: "constructor",
  },
  {
    anonymous: false,
    inputs: [
      { indexed: true, internalType: "address", name: "owner", type: "address" },
      { indexed: false, internalType: "uint256", name: "amount", type: "uint256" },
    ],
    name: "FundsWithdrawn",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [{ indexed: false, internalType: "uint256", name: "newHiddenNumber", type: "uint256" }],
    name: "HiddenNumberUpdated",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [{ indexed: false, internalType: "uint256", name: "newMaxPrize", type: "uint256" }],
    name: "MaxPrizeUpdated",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      { indexed: true, internalType: "address", name: "player", type: "address" },
      { indexed: false, internalType: "bool", name: "success", type: "bool" },
      { indexed: false, internalType: "uint256", name: "amountWon", type: "uint256" },
    ],
    name: "NumberGuessed",
    type: "event",
  },
  {
    inputs: [],
    name: "getMaxPrize",
    outputs: [{ internalType: "uint256", name: "", type: "uint256" }],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "maxPrize",
    outputs: [{ internalType: "uint256", name: "", type: "uint256" }],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "owner",
    outputs: [{ internalType: "address", name: "", type: "address" }],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [{ internalType: "uint256", name: "guessedNumber", type: "uint256" }],
    name: "play",
    outputs: [],
    stateMutability: "payable",
    type: "function",
  },
  {
    inputs: [{ internalType: "uint256", name: "_hiddenNumber", type: "uint256" }],
    name: "setHiddenNumber",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [{ internalType: "uint256", name: "_maxPrize", type: "uint256" }],
    name: "setMaxPrize",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [{ internalType: "uint256", name: "amount", type: "uint256" }],
    name: "withdrawFunds",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
];

function App() {
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [contract, setContract] = useState(null);
  const [account, setAccount] = useState("");
  const [isOwner, setIsOwner] = useState(false);
  const [maxPrize, setMaxPrize] = useState("0");
  const [guessNumber, setGuessNumber] = useState("");
  const [ethAmount, setEthAmount] = useState("");
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [contractBalance, setContractBalance] = useState("0");
  const [newMaxPrize, setNewMaxPrize] = useState("");
  const [newHiddenNumber, setNewHiddenNumber] = useState("");
  const [withdrawAmount, setWithdrawAmount] = useState("");

  // 🔌 MetaMask-пен қосылу
  const connectWallet = async () => {
    if (!window.ethereum) {
      alert("MetaMask орнатылмаған!");
      return;
    }

    try {
      const newProvider = new ethers.BrowserProvider(window.ethereum);
      await newProvider.send("eth_requestAccounts", []);
      const signer = await newProvider.getSigner();
      const userAddress = await signer.getAddress();

      const contractInstance = new ethers.Contract(contractAddress, contractABI, signer);
      const owner = await contractInstance.owner();

      setProvider(newProvider);
      setSigner(signer);
      setContract(contractInstance);
      setAccount(userAddress);
      setIsOwner(userAddress.toLowerCase() === owner.toLowerCase());

      const max = await contractInstance.getMaxPrize();
      setMaxPrize(ethers.formatEther(max));

      const balance = await newProvider.getBalance(contractAddress);
      setContractBalance(ethers.formatEther(balance));
    } catch (err) {
      console.error("MetaMask қате:", err);
      setStatus("❌ MetaMask қосылу қатесі: " + err.message);
    }
  };

  useEffect(() => {
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts) => {
        if (accounts.length === 0) {
          // Аккаунт disconnected
          setAccount("");
          setIsOwner(false);
        } else {
          connectWallet();
        }
      });
    }
  }, []);

  const handlePlay = async () => {
    setStatus("");
    if (!guessNumber || !ethAmount) {
      setStatus("❌ ETH немесе сан енгізіңіз.");
      return;
    }

    setIsLoading(true);
    try {
      const tx = await contract.play(guessNumber, {
        value: ethers.parseEther(ethAmount),
      });
      await tx.wait();
      setStatus("✅ Ойын сәтті өтті! Нәтижесін тексеріңіз.");
      
      // Обновляем баланс контракта после игры
      const balance = await provider.getBalance(contractAddress);
      setContractBalance(ethers.formatEther(balance));
    } catch (err) {
      setStatus("❌ Транзакция қатесі: " + (err.reason || err.message));
    }
    setIsLoading(false);
  };

  const handleSetMaxPrize = async () => {
    setStatus("");
    if (!newMaxPrize) {
      setStatus("❌ Жаңа maxPrize мәнін енгізіңіз");
      return;
    }

    try {
      const balance = await provider.getBalance(contractAddress);
      const newMax = ethers.parseEther(newMaxPrize);

      if (newMax > balance / 2n) {
        setStatus("❌ maxPrize ≥ balance / 2 шартын бұзады.");
        return;
      }

      setIsLoading(true);
      const tx = await contract.setMaxPrize(newMax);
      await tx.wait();
      const updated = await contract.getMaxPrize();
      setMaxPrize(ethers.formatEther(updated));
      setStatus("✅ maxPrize жаңартылды!");
    } catch (err) {
      setStatus("❌ Қате: " + (err.reason || err.message));
    }
    setIsLoading(false);
  };

  const handleSetHiddenNumber = async () => {
    setStatus("");
    if (!newHiddenNumber) {
      setStatus("❌ Жаңа жасырын санды енгізіңіз");
      return;
    }

    try {
      setIsLoading(true);
      const tx = await contract.setHiddenNumber(newHiddenNumber);
      await tx.wait();
      setStatus("✅ Жасырын сан жаңартылды!");
    } catch (err) {
      setStatus("❌ Қате: " + (err.reason || err.message));
    }
    setIsLoading(false);
  };

  const handleWithdraw = async () => {
    setStatus("");
    if (!withdrawAmount) {
      setStatus("❌ Шығарылатын соманы енгізіңіз");
      return;
    }

    try {
      const balance = await provider.getBalance(contractAddress);
      const max = await contract.getMaxPrize();
      const amount = ethers.parseEther(withdrawAmount);

      if (max > (balance - amount) / 2n) {
        setStatus("❌ Шарт бұзылады: maxPrize ≥ баланс / 2 болуы керек.");
        return;
      }

      setIsLoading(true);
      const tx = await contract.withdrawFunds(amount);
      await tx.wait();
      const newBalance = await provider.getBalance(contractAddress);
      setContractBalance(ethers.formatEther(newBalance));
      setStatus("✅ Қаражат шығарылды!");
    } catch (err) {
      setStatus("❌ Қате: " + (err.reason || err.message));
    }
    setIsLoading(false);
  };

  return (
    <div className="p-6 max-w-xl mx-auto font-sans space-y-4">
      <h1 className="text-2xl font-bold">🎯 Лотерея: Санды тап</h1>
      
      {!account ? (
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded mb-4"
          onClick={connectWallet}
        >
          🔌 MetaMask-ке қосылу
        </button>
      ) : (
        <>
          <p>👛 Аккаунт: {account}</p>
          <p>💰 maxPrize: {maxPrize} ETH</p>
          <p>📦 Контракт балансы: {contractBalance} ETH</p>

          <div className="border p-4 rounded shadow space-y-2">
            <h2 className="font-semibold">🎮 Ойын</h2>
            <input
              className="border rounded p-1 w-full"
              placeholder="Санды енгіз (мысалы: 7)"
              type="number"
              value={guessNumber}
              onChange={(e) => setGuessNumber(e.target.value)}
            />
            <input
              className="border rounded p-1 w-full"
              placeholder="ETH (мысалы: 0.01)"
              type="number"
              value={ethAmount}
              onChange={(e) => setEthAmount(e.target.value)}
            />
            <button
              className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
              onClick={handlePlay}
              disabled={isLoading || !account}
            >
              {isLoading ? "Жүктелуде..." : "Ойнау"}
            </button>
          </div>

          {isOwner && (
            <div className="border p-4 rounded shadow bg-gray-100 space-y-4">
              <h2 className="font-semibold">🛠️ Админ панелі</h2>

              <div>
                <input
                  className="border rounded p-1 w-full"
                  placeholder="Жаңа maxPrize (ETH)"
                  value={newMaxPrize}
                  onChange={(e) => setNewMaxPrize(e.target.value)}
                  type="number"
                />
                <button
                  className="bg-green-600 text-white px-4 py-2 rounded mt-2 disabled:opacity-50"
                  onClick={handleSetMaxPrize}
                  disabled={isLoading}
                >
                  {isLoading ? "Жүктелуде..." : "MaxPrize жаңарту"}
                </button>
              </div>

              <div>
                <input
                  className="border rounded p-1 w-full"
                  placeholder="Жаңа жасырын сан"
                  value={newHiddenNumber}
                  onChange={(e) => setNewHiddenNumber(e.target.value)}
                  type="number"
                />
                <button
                  className="bg-yellow-500 text-white px-4 py-2 rounded mt-2 disabled:opacity-50"
                  onClick={handleSetHiddenNumber}
                  disabled={isLoading}
                >
                  {isLoading ? "Жүктелуде..." : "Жасырын сан орнату"}
                </button>
              </div>

              <div>
                <input
                  className="border rounded p-1 w-full"
                  placeholder="Шығарылатын ETH сомасы"
                  value={withdrawAmount}
                  onChange={(e) => setWithdrawAmount(e.target.value)}
                  type="number"
                />
                <button
                  className="bg-red-500 text-white px-4 py-2 rounded mt-2 disabled:opacity-50"
                  onClick={handleWithdraw}
                  disabled={isLoading}
                >
                  {isLoading ? "Жүктелуде..." : "Қаражат шығару"}
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {status && <div className="p-2 bg-gray-200 border rounded">{status}</div>}
    </div>
  );
}

export default App;
