Imports System
Imports System.Net
Imports System.IO
Imports System.Text
Imports System.Threading.Tasks
Imports System.Text.Json
Imports Npgsql

Module Program

    '==========================================================================
    ' Microservicio TEMAS y AUTORES proyecto OverSounds - GPS 2025-2026
    ' Creado por: José Manuel de Torres Dominguez
    '==========================================================================
    ' PARÁMETROS DE CONFIGURACIÓN
    Dim host_ip As String = "+"
    Dim host_port As Integer = 8081
    Dim connectionString = "Host=pgnweb.ddns.net;Username=tya_admin;Password=12345;Database=tya"
    Dim db As NpgsqlDataSource = Nothing
    Dim ip_auth As String = "localhost:8080" ' IP del servicio de autenticación
    '==========================================================================

    Sub Main(args As String())
        ' Conectarse a la base de datos PostgreSQL
        Try
            db = NpgsqlDataSource.Create(connectionString)
            Console.WriteLine("Conexión a la base de datos PostgreSQL establecida correctamente.")
        Catch ex As Exception
            Console.WriteLine("Error al conectar a la base de datos PostgreSQL: " & ex.Message)
            Return
        End Try

        ' Iniciar el servidor de manera asíncrona
        StartServerAsync(host_ip, host_port).GetAwaiter().GetResult()
    End Sub


    Async Function StartServerAsync(host_ip As String, host_port As Integer) As Task
        ' Crear el servidor HTTP
        Dim listener As New HttpListener()
        ' Configurar el prefijo (URL base) donde escuchar
        listener.Prefixes.Add("http://" + host_ip + ":" + host_port.ToString() + "/")

        Try
            ' Iniciar el servidor
            listener.Start()
            Console.WriteLine("Servidor HTTP iniciado en http://" + host_ip + ":" + host_port.ToString())
            Console.WriteLine("Presiona Ctrl+C para detener el servidor")
            Console.WriteLine()

            ' Bucle principal para manejar peticiones
            While True
                ' Esperar por una petición de manera asíncrona
                Dim context As HttpListenerContext = Await listener.GetContextAsync()

                ' Manejar cada petición en una tarea separada (sin esperar a que termine)
                Dim fireAndForget = Task.Run(Async Function()
                                                 Await HandleRequestAsync(context.Request, context.Response)
                                             End Function)
            End While

        Catch ex As Exception
            Console.WriteLine($"Error: {ex.Message}")
        Finally
            ' Detener el servidor
            Console.WriteLine("Servidor detenido")
        End Try
    End Function


    Async Function HandleRequestAsync(request As HttpListenerRequest, response As HttpListenerResponse) As Task
        Dim jsonResponse As String = GenerateErrorResponse("501", "No implementado")
        Dim contentType = "application/json"
        Dim statusCode As Integer = HttpStatusCode.OK
        Dim URLpath As String() = request.Url.AbsolutePath.Split("/"c) ' Ejemplo: /song/123

        Try
            ' Mostrar información de la petición
            Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Petición recibida: {request.HttpMethod} {request.Url.AbsolutePath}")

            ' Obtener segmentos de la URL de manera segura
            Dim resource As String = If(URLpath.Length > 1, URLpath(1), "")
            Dim action As String = If(URLpath.Length > 2, URLpath(2), "")

            ' Servir archivos estáticos desde /static
            If resource = "static" AndAlso request.HttpMethod = "GET" Then
                ServeStaticFile(request, response)
                Return
            End If

            ' Verificar si el endpoint requiere autenticación
            ' Todos los endpoints GET no requieren autenticación
            ' Solo POST, PATCH, DELETE requieren autenticación
            Dim userId As Integer? = Nothing
            If request.HttpMethod <> "GET" Then
                ' Validar el token de autenticación
                userId = Await ValidateAuthTokenAsync(request)

                If Not userId.HasValue Then
                    ' No autenticado o token inválido
                    jsonResponse = GenerateErrorResponse("401", "No autenticado. Se requiere iniciar sesión")
                    statusCode = HttpStatusCode.Unauthorized

                    ' Configurar y enviar la respuesta
                    response.StatusCode = statusCode
                    response.ContentType = contentType
                    Dim buffer2 As Byte() = Encoding.UTF8.GetBytes(jsonResponse)
                    response.ContentLength64 = buffer2.Length
                    Dim output2 As Stream = response.OutputStream
                    Await output2.WriteAsync(buffer2, 0, buffer2.Length)
                    output2.Close()

                    Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Acceso denegado - No autenticado")
                    Console.WriteLine()
                    Return
                End If

                Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Usuario autenticado: {userId.Value}")
            End If

            ' Detectar la ruta personalizada
            If resource = "song" Then

                If action = "upload" AndAlso request.HttpMethod = "POST" Then
                    uploadSong(request, action, jsonResponse, statusCode, userId.Value)
                End if

                ' Ruta no encontrada
                jsonResponse = GenerateErrorResponse("404", "Recurso no encontrado")
                statusCode = HttpStatusCode.NotFound


            ElseIf resource = "album" Then

                ' Ruta no encontrada
                jsonResponse = GenerateErrorResponse("404", "Recurso no encontrado")
                statusCode = HttpStatusCode.NotFound


            ElseIf resource = "merch" Then

                ' Ruta no encontrada
                jsonResponse = GenerateErrorResponse("404", "Recurso no encontrado")
                statusCode = HttpStatusCode.NotFound


            ElseIf resource = "artist" Then

                ' Ruta no encontrada
                jsonResponse = GenerateErrorResponse("404", "Recurso no encontrado")
                statusCode = HttpStatusCode.NotFound


            ElseIf resource = "genres" AndAlso request.HttpMethod = "GET" Then
                ' Endpoint /genres - no requiere autenticación
                ' getGenres(request, action, jsonResponse, statusCode) ' Eliminado


            ElseIf request.Url.AbsolutePath = "/" Then
                ' Ruta raíz
                jsonResponse = ConvertToJson("Microservicio TEMAS y AUTORES proyecto OverSounds - GPS 2025-2026\nCreado por: José Manuel de Torres Dominguez")
                statusCode = HttpStatusCode.OK


            Else
                ' Ruta no encontrada
                jsonResponse = GenerateErrorResponse("404", "Recurso no encontrado")
                statusCode = HttpStatusCode.NotFound
            End If


            ' Configurar la respuesta
            response.StatusCode = statusCode
            response.ContentType = contentType
            Dim buffer As Byte() = Encoding.UTF8.GetBytes(jsonResponse)
            response.ContentLength64 = buffer.Length

            ' Enviar la respuesta de manera asíncrona
            Dim output As Stream = response.OutputStream
            Await output.WriteAsync(buffer, 0, buffer.Length)
            output.Close()

            Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Respuesta enviada: {statusCode} - {jsonResponse.Replace(Environment.NewLine, "")}")
            Console.WriteLine()

        Catch ex As Exception
            Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Error procesando petición: {ex.Message}")
            Console.WriteLine(ex.ToString)

            Try
                response.StatusCode = 500
                response.Close()
            Catch
                ' Ignorar errores al cerrar la respuesta
            End Try
        End Try
    End Function

    ' Función helper para convertir lista de Strings a JSON
    Function ConvertToJson(obj As Object) As String
        Dim options As New JsonSerializerOptions With {.WriteIndented = True}
        Return JsonSerializer.Serialize(obj, options)
    End Function

    ' Funcion helper para generar una respuesta error JSON
    Function GenerateErrorResponse(code As String, message As String) As String
        Dim errorObj As New Dictionary(Of String, String) From {{"code", code}, {"message", message}}
        Return ConvertToJson(errorObj)
    End Function

    ' Función para validar el token de autenticación
    Async Function ValidateAuthTokenAsync(request As HttpListenerRequest) As Task(Of Integer?)
        Try
            ' Buscar la cookie oversound_auth
            Dim authCookie As Cookie = Nothing
            If request.Cookies IsNot Nothing Then
                authCookie = request.Cookies("oversound_auth")
            End If

            If authCookie Is Nothing OrElse String.IsNullOrEmpty(authCookie.Value) Then
                Return Nothing ' No hay token
            End If

            Dim token As String = authCookie.Value
            Dim authUrl As String = $"http://{ip_auth}/auth"
            Dim timeout As TimeSpan = TimeSpan.FromSeconds(2)

            Using httpClient As New Net.Http.HttpClient()
                httpClient.Timeout = timeout

                ' Crear el request con la cookie en el header
                Dim requestMessage As New Net.Http.HttpRequestMessage(Net.Http.HttpMethod.Get, authUrl)
                requestMessage.Headers.Add("Cookie", $"oversound_auth={token}")

                Dim authResponse = Await httpClient.SendAsync(requestMessage)

                If authResponse.StatusCode = Net.HttpStatusCode.OK Then
                    ' Leer los datos del usuario
                    Dim responseBody As String = Await authResponse.Content.ReadAsStringAsync()
                    Dim userData = JsonSerializer.Deserialize(Of Dictionary(Of String, JsonElement))(responseBody)
                    ' Extraer solo el userId
                    If userData.ContainsKey("userId") Then
                        Return userData("userId").GetInt32()
                    End If

                    Return Nothing
                Else
                    Console.WriteLine($"Auth service returned status: {authResponse.StatusCode}")
                    Return Nothing ' Token inválido
                End If
            End Using

        Catch ex As Exception
            Console.WriteLine($"Error al validar token: {ex.Message}")
            Return Nothing
        End Try
    End Function

    '==========================================================================
    ' LÓGICA DE NEGOCIO
    '==========================================================================

    ' Función auxiliar para obtener el ID del artista asociado a un usuario
    Function GetArtistIdByUserId(userId As Integer) As Integer?
        Try
            Using cmd = db.CreateCommand("SELECT idartista FROM artistas WHERE userid = @userid")
                cmd.Parameters.AddWithValue("@userid", userId)
                Dim result = cmd.ExecuteScalar()
                If result IsNot Nothing AndAlso Not IsDBNull(result) Then
                    Return CInt(result)
                End If
            End Using
        Catch ex As Exception
            Console.WriteLine($"Error al buscar artista por userId: {ex.Message}")
        End Try
        Return Nothing
    End Function


    '==========================================================================
    ' FUNCIONES AUXILIARES COMUNES
    '==========================================================================

    ''' <summary>
    ''' Valida que un action sea un ID numérico válido
    ''' </summary>
    Function ValidateNumericId(action As String, resourceName As String, ByRef jsonResponse As String, ByRef statusCode As Integer) As Integer?
        If Not IsNumeric(action) Then
            jsonResponse = GenerateErrorResponse("400", $"ID de {resourceName} inválido")
            statusCode = HttpStatusCode.BadRequest
            Return Nothing
        End If
        Return Integer.Parse(action)
    End Function


    ''' <summary>
    ''' Recupera una lista de IDs desde una query SQL
    ''' </summary>
    Function GetIdList(query As String, paramName As String, paramValue As Integer) As List(Of Integer)
        Dim results As New List(Of Integer)
        Using cmd = db.CreateCommand(query)
            cmd.Parameters.AddWithValue(paramName, paramValue)
            Using reader = cmd.ExecuteReader()
                While reader.Read()
                    results.Add(reader.GetInt32(0))
                End While
            End Using
        End Using
        Return results
    End Function

    ''' <summary>
    ''' Obtiene la ruta de una imagen desde la base de datos antes de eliminar un registro
    ''' </summary>
    Function GetImagePathBeforeDelete(tableName As String, imageColumnName As String, idColumnName As String, idValue As Integer) As String
        Dim imagePath As String = Nothing
        Using cmd = db.CreateCommand($"SELECT {imageColumnName} FROM {tableName} WHERE {idColumnName} = @id")
            cmd.Parameters.AddWithValue("@id", idValue)
            Dim result As Object = cmd.ExecuteScalar()
            If result IsNot Nothing AndAlso Not IsDBNull(result) Then
                imagePath = result.ToString()
            End If
        End Using
        Return imagePath
    End Function

    ''' <summary>
    ''' Elimina un registro y su imagen asociada
    ''' </summary>
    Function DeleteRecordWithImage(tableName As String, idColumnName As String, idValue As Integer, imagePath As String, resourceName As String, ByRef jsonResponse As String, ByRef statusCode As Integer) As Boolean
        Using cmd = db.CreateCommand($"DELETE FROM {tableName} WHERE {idColumnName} = @id")
            cmd.Parameters.AddWithValue("@id", idValue)
            Dim rowsAffected As Integer = cmd.ExecuteNonQuery()

            If rowsAffected = 0 Then
                jsonResponse = GenerateErrorResponse("404", $"{resourceName} no encontrado")
                statusCode = HttpStatusCode.NotFound
                Return False
            Else
                ' Eliminar archivo de imagen si existe
                If imagePath IsNot Nothing Then
                    DeleteImageFile(imagePath)
                End If

                jsonResponse = ""
                statusCode = HttpStatusCode.OK
                Return True
            End If
        End Using
    End Function

    ''' <summary>
    ''' Lee el cuerpo de una solicitud HTTP como texto
    ''' </summary>
    Function ReadRequestBody(request As HttpListenerRequest) As String
        Using reader As New StreamReader(request.InputStream, request.ContentEncoding)
            Return reader.ReadToEnd()
        End Using
    End Function

    '==========================================================================
    ' MÉTODOS PARA SONG
    '==========================================================================
    Sub uploadSong(request As HttpListenerRequest, action As String, ByRef jsonResponse As String, ByRef statusCode As Integer, userId As Integer)
        Try
            ' Leer el body del request
            Dim body As String
            Using reader As New StreamReader(request.InputStream, request.ContentEncoding)
                body = reader.ReadToEnd()
            End Using

            ' Parsear el JSON
            Dim songData = JsonSerializer.Deserialize(Of Dictionary(Of String, JsonElement))(body)

            ' Validar campos requeridos
            If Not songData.ContainsKey("title") OrElse Not songData.ContainsKey("genres") OrElse
               Not songData.ContainsKey("cover") OrElse Not songData.ContainsKey("price") OrElse
               Not songData.ContainsKey("trackId") OrElse Not songData.ContainsKey("duration") Then
                jsonResponse = GenerateErrorResponse("400", "Faltan campos requeridos")
                statusCode = HttpStatusCode.BadRequest
                Return
            End If

            ' Obtener valores
            Dim title As String = songData("title").GetString()
            Dim description As String = If(songData.ContainsKey("description") AndAlso songData("description").ValueKind <> JsonValueKind.Null, songData("description").GetString(), Nothing)
            Dim cover As String = If(songData.ContainsKey("cover") AndAlso songData("cover").ValueKind <> JsonValueKind.Null AndAlso Not String.IsNullOrWhiteSpace(songData("cover").GetString()), songData("cover").GetString(), Nothing)
            Dim price As Decimal = songData("price").GetDecimal()
            Dim albumId As Integer? = If(songData.ContainsKey("albumId") AndAlso songData("albumId").ValueKind <> JsonValueKind.Null, CType(songData("albumId").GetInt32(), Integer?), Nothing)
            Dim albumOrder As Integer? = If(songData.ContainsKey("albumOrder") AndAlso songData("albumOrder").ValueKind <> JsonValueKind.Null, CType(songData("albumOrder").GetInt32(), Integer?), Nothing)
            Dim releaseDate As String = If(songData.ContainsKey("releaseDate"), songData("releaseDate").GetString(), DateTime.Now.ToString("yyyy-MM-dd"))
            Dim trackId As Integer = songData("trackId").GetInt32()
            Dim duration As Integer = songData("duration").GetInt32()

            ' Validar que price sea positivo
            If price <= 0 Then
                jsonResponse = GenerateErrorResponse("400", "El precio debe ser un valor positivo")
                statusCode = HttpStatusCode.BadRequest
                Return
            End If

            ' Validar que si albumId está definido, albumOrder también lo esté
            If albumId.HasValue AndAlso Not albumOrder.HasValue Then
                jsonResponse = GenerateErrorResponse("400", "Si se especifica albumId, también se debe especificar albumOrder")
                statusCode = HttpStatusCode.BadRequest
                Return
            End If

            If Not albumId.HasValue AndAlso albumOrder.HasValue Then
                jsonResponse = GenerateErrorResponse("400", "Si se especifica albumOrder, también se debe especificar albumId")
                statusCode = HttpStatusCode.BadRequest
                Return
            End If

            ' Validar que el álbum exista si se especifica
            If albumId.HasValue Then
                Dim albumExists As Boolean = False
                Using cmd = db.CreateCommand("SELECT COUNT(*) FROM albumes WHERE idalbum = @idalbum")
                    cmd.Parameters.AddWithValue("@idalbum", albumId.Value)
                    Dim count As Integer = CInt(cmd.ExecuteScalar())
                    albumExists = count > 0
                End Using

                If Not albumExists Then
                    jsonResponse = GenerateErrorResponse("422", "El álbum especificado no existe")
                    statusCode = 422 ' Unprocessable Entity
                    Return
                End If
            End If

            ' Insertar canción con albumog (el álbum original) con cover por defecto
            Dim newSongId As Integer
            Using cmd = db.CreateCommand("INSERT INTO canciones (titulo, descripcion, cover, track, duracion, fechalanzamiento, precio, albumog) VALUES (@titulo, @descripcion, @cover, @track, @duracion, @fecha, @precio, @albumog) RETURNING idcancion")
                cmd.Parameters.AddWithValue("@titulo", title)
                cmd.Parameters.AddWithValue("@descripcion", If(description, DBNull.Value))
                cmd.Parameters.AddWithValue("@cover", "/song/default.png")
                cmd.Parameters.AddWithValue("@track", trackId)
                cmd.Parameters.AddWithValue("@duracion", duration)
                cmd.Parameters.AddWithValue("@fecha", Date.Parse(releaseDate))
                cmd.Parameters.AddWithValue("@precio", price)
                cmd.Parameters.AddWithValue("@albumog", If(albumId.HasValue, CType(albumId.Value, Object), DBNull.Value))
                newSongId = CInt(cmd.ExecuteScalar())
            End Using

            ' Guardar imagen y actualizar cover con la ruta si se proporcionó
            If cover IsNot Nothing Then
                Dim coverPath As String = SaveBase64Image(cover, "song", newSongId)
                If coverPath IsNot Nothing Then
                    Using cmd = db.CreateCommand("UPDATE canciones SET cover = @cover WHERE idcancion = @id")
                        cmd.Parameters.AddWithValue("@cover", coverPath)
                        cmd.Parameters.AddWithValue("@id", newSongId)
                        cmd.ExecuteNonQuery()
                    End Using
                End If
            End If

            ' Obtener el ID del artista asociado al usuario autenticado
            Dim artistId As Integer? = GetArtistIdByUserId(userId)

            If Not artistId.HasValue Then
                jsonResponse = GenerateErrorResponse("403", "El usuario no tiene un artista asociado")
                statusCode = HttpStatusCode.Forbidden
                Return
            End If

            ' Insertar al artista principal (el usuario autenticado) - NO es colaborador (ft = false)
            Using cmd = db.CreateCommand("INSERT INTO autorescanciones (idartista, idcancion, ft) VALUES (@idartista, @idcancion, @ft)")
                cmd.Parameters.AddWithValue("@idartista", artistId.Value)
                cmd.Parameters.AddWithValue("@idcancion", newSongId)
                cmd.Parameters.AddWithValue("@ft", False) ' No es colaborador, es el artista principal
                cmd.ExecuteNonQuery()
            End Using

            ' Validar y insertar géneros
            If songData.ContainsKey("genres") Then
                For Each genreElement In songData("genres").EnumerateArray()
                    Dim genreId As Integer = genreElement.GetInt32()

                    ' Validar que el género exista
                    Dim genreExists As Boolean = False
                    Using cmd = db.CreateCommand("SELECT COUNT(*) FROM generos WHERE idgenero = @idgenero")
                        cmd.Parameters.AddWithValue("@idgenero", genreId)
                        Dim count As Integer = CInt(cmd.ExecuteScalar())
                        genreExists = count > 0
                    End Using

                    If Not genreExists Then
                        jsonResponse = GenerateErrorResponse("422", $"El género con ID {genreId} no existe")
                        statusCode = 422 ' Unprocessable Entity
                        Return
                    End If

                    Using cmd = db.CreateCommand("INSERT INTO generoscanciones (idcancion, idgenero) VALUES (@idcancion, @idgenero)")
                        cmd.Parameters.AddWithValue("@idcancion", newSongId)
                        cmd.Parameters.AddWithValue("@idgenero", genreId)
                        cmd.ExecuteNonQuery()
                    End Using
                Next
            End If

            ' Insertar colaboradores (artistas con ft = true)
            If songData.ContainsKey("collaborators") Then
                For Each collabElement In songData("collaborators").EnumerateArray()
                    Dim collabArtistId As Integer = collabElement.GetInt32()
                    Using cmd = db.CreateCommand("INSERT INTO autorescanciones (idartista, idcancion, ft) VALUES (@idartista, @idcancion, @ft)")
                        cmd.Parameters.AddWithValue("@idartista", collabArtistId)
                        cmd.Parameters.AddWithValue("@idcancion", newSongId)
                        cmd.Parameters.AddWithValue("@ft", True) ' Es colaborador
                        cmd.ExecuteNonQuery()
                    End Using
                Next
            End If

            ' Si tiene álbum original (albumog), SIEMPRE insertar en CancionesAlbumes
            ' Esto asegura que el álbum original siempre aparezca en la tabla de relaciones
            If albumId.HasValue Then
                ' albumOrder es obligatorio cuando se proporciona albumId
                If Not albumOrder.HasValue Then
                    jsonResponse = GenerateErrorResponse("400", "Si se especifica albumId, también se debe especificar albumOrder")
                    statusCode = HttpStatusCode.BadRequest
                    Return
                End If

                Using cmd = db.CreateCommand("INSERT INTO cancionesalbumes (idcancion, idalbum, tracknumber) VALUES (@idcancion, @idalbum, @tracknumber)")
                    cmd.Parameters.AddWithValue("@idcancion", newSongId)
                    cmd.Parameters.AddWithValue("@idalbum", albumId.Value)
                    cmd.Parameters.AddWithValue("@tracknumber", albumOrder.Value)
                    cmd.ExecuteNonQuery()
                End Using
            End If

            jsonResponse = ConvertToJson(New Dictionary(Of String, Object) From {{"songId", newSongId}})
            statusCode = HttpStatusCode.OK

        Catch ex As Exception
            jsonResponse = GenerateErrorResponse("500", "Error al crear la canción: " & ex.Message)
            statusCode = HttpStatusCode.InternalServerError
        End Try
    End Sub


    ' ==========================================================================
    ' FUNCIONES HELPER PARA CONVERSIÓN DE IMÁGENES
    ' ==========================================================================

    ''' <summary>
    ''' Convierte una cadena a bytes. Soporta base64 puro o data URI completo.
    ''' Si la conversión base64 falla, convierte como texto UTF8.
    ''' </summary>
    ''' <param name="input">Cadena a convertir (puede incluir prefijo data:image/...;base64,)</param>
    ''' <returns>Array de bytes</returns>
    Function StringToBytes(input As String) As Byte()
        If String.IsNullOrEmpty(input) Then
            Return New Byte() {}
        End If

        Try
            ' Si tiene el prefijo data:image, extraer solo la parte base64
            Dim base64String As String = input
            If input.Contains(",") Then
                ' Formato: data:image/png;base64,iVBORw0KGgo...
                base64String = input.Substring(input.IndexOf(",") + 1)
            End If

            ' Intentar convertir desde base64
            Return Convert.FromBase64String(base64String)
        Catch ex As FormatException
            ' Si falla, convertir como texto UTF8
            Return Encoding.UTF8.GetBytes(input)
        End Try
    End Function

    ''' <summary>
    ''' Convierte bytes a cadena base64 con prefijo data URI.
    ''' </summary>
    ''' <param name="bytes">Array de bytes a convertir</param>
    ''' <returns>Cadena en formato data:image/png;base64,...</returns>
    Function BytesToString(bytes As Byte()) As String
        If bytes Is Nothing OrElse bytes.Length = 0 Then
            Return ""
        End If
        Return "data:image/png;base64," & Convert.ToBase64String(bytes)
    End Function

    ''' <summary>
    ''' Guarda una imagen en base64 en la carpeta static y devuelve la ruta relativa.
    ''' </summary>
    ''' <param name="base64Image">Cadena de imagen en base64 (con o sin prefijo data:image)</param>
    ''' <param name="subfolder">Subcarpeta dentro de static (songs, albums, merch, artists)</param>
    ''' <param name="id">ID único del elemento para el nombre del archivo</param>
    ''' <returns>Ruta relativa desde static (ej: /songs/123.png)</returns>
    Function SaveBase64Image(base64Image As String, subfolder As String, id As Integer) As String
        Try
            ' Extraer la extensión del prefijo data:image
            Dim extension As String = "png" ' Por defecto PNG
            Dim base64Data As String = base64Image

            If base64Image.StartsWith("data:image/") Then
                Dim semicolonIndex As Integer = base64Image.IndexOf(";")
                If semicolonIndex > 0 Then
                    Dim mimeType As String = base64Image.Substring(11, semicolonIndex - 11) ' Después de "data:image/"
                    extension = mimeType.ToLower()
                End If

                Dim commaIndex As Integer = base64Image.IndexOf(",")
                If commaIndex > 0 Then
                    base64Data = base64Image.Substring(commaIndex + 1)
                End If
            End If

            ' Convertir base64 a bytes
            Dim imageBytes As Byte() = Convert.FromBase64String(base64Data)

            ' Crear ruta completa
            Dim staticPath As String = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "static", subfolder)
            If Not Directory.Exists(staticPath) Then
                Directory.CreateDirectory(staticPath)
            End If

            Dim fileName As String = $"{id}.{extension}"
            Dim fullPath As String = Path.Combine(staticPath, fileName)
            Console.WriteLine($"Guardando imagen en: {fullPath}")

            ' Guardar archivo
            File.WriteAllBytes(fullPath, imageBytes)

            ' Devolver ruta relativa (desde static)
            Return $"/{subfolder}/{fileName}"

        Catch ex As Exception
            Console.WriteLine($"Error al guardar imagen: {ex.Message}")
            Return Nothing
        End Try
    End Function

    ''' <summary>
    ''' Elimina un archivo de imagen de la carpeta static.
    ''' </summary>
    ''' <param name="relativePath">Ruta relativa desde static (ej: /songs/123.png)</param>
    Sub DeleteImageFile(relativePath As String)
        Try
            If String.IsNullOrEmpty(relativePath) Then
                Return
            End If

            ' Construir ruta completa
            Dim staticPath As String = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "static")
            Dim fullPath As String = Path.Combine(staticPath, relativePath.TrimStart("/"c))

            If File.Exists(fullPath) Then
                File.Delete(fullPath)
                Console.WriteLine($"Imagen eliminada: {fullPath}")
            End If

        Catch ex As Exception
            Console.WriteLine($"Error al eliminar imagen: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Obtiene la ruta de imagen almacenada en la base de datos.
    ''' Si es NULL, vacío o string vacío, devuelve Nothing.
    ''' </summary>
    ''' <param name="imagePath">Ruta desde la base de datos</param>
    ''' <returns>Ruta relativa o Nothing</returns>
    Function GetImagePath(imagePath As Object) As String
        If imagePath Is Nothing OrElse IsDBNull(imagePath) Then
            Return Nothing
        End If

        Dim path As String = imagePath.ToString()
        If String.IsNullOrEmpty(path) OrElse path.Trim() = "" OrElse path = "default.png" OrElse path.EndsWith("/default.png") Then
            Return Nothing
        End If

        Return path
    End Function

    ''' <summary>
    ''' Sirve archivos estáticos desde la carpeta static
    ''' </summary>
    Sub ServeStaticFile(request As HttpListenerRequest, response As HttpListenerResponse)
        Try
            ' Obtener la ruta relativa desde /static/...
            Dim requestPath As String = request.Url.AbsolutePath

            ' Construir ruta completa del archivo
            Dim staticPath As String = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "static")
            Dim filePath As String = Path.Combine(staticPath, requestPath.Replace("/static/", "").Replace("/", Path.DirectorySeparatorChar.ToString()))

            ' Verificar que el archivo existe y está dentro de la carpeta static (seguridad)
            Dim fullStaticPath As String = Path.GetFullPath(staticPath)
            Dim fullFilePath As String = Path.GetFullPath(filePath)

            If Not fullFilePath.StartsWith(fullStaticPath) Then
                ' Intento de acceso fuera de la carpeta static
                response.StatusCode = HttpStatusCode.Forbidden
                response.Close()
                Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Acceso denegado: intento de acceder fuera de static")
                Return
            End If

            If Not File.Exists(fullFilePath) Then
                ' Archivo no encontrado
                response.StatusCode = HttpStatusCode.NotFound
                Dim errorBytes As Byte() = Encoding.UTF8.GetBytes("File not found")
                response.ContentLength64 = errorBytes.Length
                response.OutputStream.Write(errorBytes, 0, errorBytes.Length)
                response.Close()
                Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Archivo no encontrado: {requestPath}")
                Return
            End If

            ' Determinar Content-Type basado en la extensión
            Dim extension As String = Path.GetExtension(fullFilePath).ToLower()
            Dim contentType As String = "application/octet-stream"

            Select Case extension
                Case ".png"
                    contentType = "image/png"
                Case ".jpg", ".jpeg"
                    contentType = "image/jpeg"
                Case ".gif"
                    contentType = "image/gif"
                Case ".svg"
                    contentType = "image/svg+xml"
                Case ".webp"
                    contentType = "image/webp"
                Case ".ico"
                    contentType = "image/x-icon"
            End Select

            ' Leer y enviar el archivo
            Dim fileBytes As Byte() = File.ReadAllBytes(fullFilePath)
            response.ContentType = contentType
            response.ContentLength64 = fileBytes.Length
            response.StatusCode = HttpStatusCode.OK
            response.OutputStream.Write(fileBytes, 0, fileBytes.Length)
            response.Close()

            Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Archivo servido: {requestPath} ({fileBytes.Length} bytes)")

        Catch ex As Exception
            Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] Error al servir archivo estático: {ex.Message}")
            response.StatusCode = HttpStatusCode.InternalServerError
            response.Close()
        End Try
    End Sub

End Module
