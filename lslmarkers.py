import pylsl
import numpy as np
import csv
import matplotlib.pyplot as plt

# Resuelve todos los streams disponibles
all_streams = pylsl.resolve_streams()
for stream_info in all_streams:
    print("Stream Name:", stream_info.name())
    print("Stream Type:", stream_info.type())

# Configura la búsqueda de streams LSL para EEG y marcadores
eeg_stream_info = pylsl.resolve_stream("type", "signal")
marker_stream_info = pylsl.resolve_stream("type", "Markers")

# Abre el primer stream EEG y el stream de marcadores encontrados
eeg_inlet = pylsl.StreamInlet(eeg_stream_info[0])
marker_inlet = pylsl.StreamInlet(marker_stream_info[0])

# Configura la figura para la visualización en tiempo real
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
fig.suptitle("EEG and Marker Data")

# Configura listas para almacenar datos de EEG y marcadores
eeg_data = []
markers = []

# Nombres de los archivos CSV para guardar los datos
eeg_csv_filename = 'eeg_data.csv'
marker_csv_filename = 'marker_data.csv'

try:
    # Abre archivos CSV para escribir los datos
    with open(eeg_csv_filename, 'w', newline='') as eeg_csvfile, \
         open(marker_csv_filename, 'w', newline='') as marker_csvfile:
        eeg_csv_writer = csv.writer(eeg_csvfile)
        marker_csv_writer = csv.writer(marker_csvfile)

        while True:
            # Recibe muestras del stream EEG
            eeg_sample, eeg_timestamp = eeg_inlet.pull_sample()

            # Recibe marcadores (eventos) del stream de marcadores
            try:
                marker_sample, marker_timestamp = marker_inlet.pull_sample()
                # Print the received marker and its timestamp
                print(f"Marker: {marker_sample[0]}, Timestamp: {marker_timestamp}")

                # Agrega el marcador a la lista de marcadores
                markers.append(marker_sample[0])

                if len(markers) > 200:
                    markers.pop(0)

                # Escribe la información en los archivos CSV respectivos
                
                marker_csv_writer.writerow([marker_timestamp, marker_sample[0]])
            

            except pylsl.LostError:
                pass
            
            # Agrega la muestra de EEG a la lista de datos
            eeg_csv_writer.writerow([eeg_timestamp] + eeg_sample)
            eeg_data.append(eeg_sample)

            # Limita la cantidad de datos que se muestran para evitar problemas de rendimiento
            if len(eeg_data) > 200:
                eeg_data.pop(0)

            # Actualiza la visualización en tiempo real
            ax1.clear()
            ax1.plot(np.arange(len(eeg_data)), eeg_data)
            ax1.set_ylabel("Valor EEG")

            ax2.clear()
            ax2.plot(np.arange(len(markers)), markers, 'ro')
            ax2.set_xlabel("Muestra")
            ax2.set_ylabel("Valor del Marcador")

            plt.pause(0.01)

except KeyboardInterrupt:
    # Cierra la conexión cuando se presiona Ctrl+C
    eeg_inlet.close_stream()
    marker_inlet.close_stream()

    # Cierra los archivos CSV
    eeg_csvfile.close()
    marker_csvfile.close()
