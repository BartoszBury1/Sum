import multiprocessing
from multiprocessing import shared_memory
import random
import numpy as np
import time

Tab = []
Check = 0

#Sumowanie elementów pojedynczych elementów w tablicy
def HalfSum(HalfTab,name):

    ShareMemo = shared_memory.SharedMemory(name=name)
    
    wynik = []
    for x in range(0, len(HalfTab), 2):
        wynik.append(HalfTab[x]+HalfTab[x+1])
    c = np.ndarray((len(HalfTab),), dtype=np.int64, buffer=ShareMemo.buf)
    while len(wynik) < len(HalfTab):
        wynik.append(0)
    c[:] = wynik[:]

    print(f"Zsumowanie elementów w procesach ze sobą: {c}")
    ShareMemo.close()


if __name__ == '__main__':
    # Losowanie elementów do naszej tablicy
    for n in range(22):
        Tab.append(random.randint(1, 200))

    #Sprawdzenie wyniku sekwencyjnie

    for number in Tab:
        Check += number
    print("=============================================")
    print(f"Poprawny wynik w sprawdzeniu sekwencyjnym {Check}")
    print("=============================================")

    nieparzysty_element = 0

#Wyrzucamy nieparzyste elementy z listy i gdy połówki list mają nieparzystą liczbę to przesuwamy index podziału by znów były parzyste
    while len(Tab) > 1:
        if len(Tab) % 2 == 1:

            nieparzysty_element += Tab.pop()
        PolListy = len(Tab) // 2

        if PolListy%2 == 0:

            Fhalf = Tab[:PolListy]
            Shalf = Tab[PolListy:]

        else:

            Fhalf = Tab[:PolListy+1]
            Shalf = Tab[PolListy+1:]

        a = np.array(Fhalf)  
        d = np.array(Shalf)
        shm1 = shared_memory.SharedMemory(create=True, size=a.nbytes)
        shm2 = shared_memory.SharedMemory(create=True, size=a.nbytes)

        # Przypisanie pamięci wspóldzielonej

        Temp1 = np.ndarray(a.shape, dtype=a.dtype, buffer=shm1.buf)
        Tamp2 = np.ndarray(d.shape, dtype=d.dtype, buffer=shm2.buf)

        Temp1[:] = a[:]  # Skopiowanie danych z tabeli
        Tamp2[:] = d[:]
        print(f"1 Tabela do sumowania = {Temp1}")
        print(f"2 Tabela do sumowania = {Tamp2}")

        P1 = multiprocessing.Process(target=HalfSum, args=(Temp1, shm1.name))
        P2 = multiprocessing.Process(target=HalfSum, args=(Tamp2, shm2.name))
        # Wystartowanie procesów
        startTime = time.time()
        P1.start()
        P2.start()

        # Czekanie aż procesy się zakończą
        P1.join()
        P2.join()

        buff1 = np.delete(Temp1, np.where(Temp1 == 0))
        Tamp2 = np.delete(Tamp2, np.where(Tamp2 == 0))
        buff1 = buff1.tolist()
        Tamp2 = Tamp2.tolist()

        # print(f"Zsumowana polowa drugiej listy = {type(buff1)}")
        # print(f"Zsumowana polowa drugiej listy = {type(Tamp2)}")

        temp = []
        if nieparzysty_element != 0:
            temp = [nieparzysty_element]
        Tab = buff1 + Tamp2 + temp
        nieparzysty_element = 0

    del Temp1, Tamp2  
    print("=============================================")
    print(f'Wynik zsumowania wspólbieznie: {Tab}')
    print("=============================================")
    endTime= time.time()
    FullTime = endTime-startTime
    print("=============================================================")
    print(f"liczenie procesami wykonało się w: {FullTime} Sec.")
    print("=============================================================")


    #Zamknięcie pamięci współdzielonej

    shm1.close()
    shm2.close()
    shm1.unlink()  
    shm2.unlink()