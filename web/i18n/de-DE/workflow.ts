const translation = {
  common: {
    undo: 'Rückgängig',
    redo: 'Wiederholen',
    editing: 'Bearbeiten',
    autoSaved: 'Automatisch gespeichert',
    unpublished: 'Nicht veröffentlicht',
    published: 'Veröffentlicht',
    publish: 'Veröffentlichen',
    update: 'Aktualisieren',
    run: 'Starten',
    running: 'Läuft',
    inRunMode: 'Im Start-Modus',
    inPreview: 'In Vorschau',
    inPreviewMode: 'Im Vorschau-Modus',
    preview: 'Vorschau',
    viewRunHistory: 'Verlauf ansehen',
    runHistory: 'Verlauf',
    goBackToEdit: 'Zurück zum Bearbeiten',
    conversationLog: 'Konversationsprotokoll',
    features: 'Funktionen',
    debugAndPreview: 'Debuggen und Vorschau',
    restart: 'Neustarten',
    currentDraft: 'Aktueller Entwurf',
    currentDraftUnpublished: 'Aktueller Entwurf nicht veröffentlicht',
    latestPublished: 'Zuletzt veröffentlicht',
    publishedAt: 'Veröffentlicht am',
    restore: 'Wiederherstellen',
    runApp: 'App starten',
    batchRunApp: 'Batch-App starten',
    accessAPIReference: 'API-Referenz aufrufen',
    embedIntoSite: 'In Website einbetten',
    addTitle: 'Titel hinzufügen...',
    addDescription: 'Beschreibung hinzufügen...',
    noVar: 'Keine Variable',
    searchVar: 'Variable suchen',
    variableNamePlaceholder: 'Variablenname',
    setVarValuePlaceholder: 'Variable festlegen',
    needConnecttip: 'Dieser Schritt ist mit nichts verbunden',
    maxTreeDepth: 'Maximale Grenze von {{depth}} Knoten pro Zweig',
    needEndNode: 'Der Endblock muss hinzugefügt werden',
    needAnswerNode: 'Der Antwortblock muss hinzugefügt werden',
    workflowProcess: 'Workflow-Prozess',
    notRunning: 'Läuft noch nicht',
    previewPlaceholder: 'Geben Sie unten Inhalte ein, um das Debugging des Chatbots zu starten',
    effectVarConfirm: {
      title: 'Variable entfernen',
      content: 'Die Variable wird in anderen Knoten verwendet. Möchten Sie sie trotzdem entfernen?',
    },
    insertVarTip: 'Drücken Sie die \'/\' Taste, um schnell einzufügen',
  },
  errorMsg: {
    fieldRequired: '{{field}} wird benötigt',
    authRequired: 'Autorisierung erforderlich',
    invalidJson: '{{field}} ist ungültiges JSON',
    fields: {
      variable: 'Variablenname',
      variableValue: 'Variablenwert',
      code: 'Code',
      model: 'Modell',
      rerankModel: 'Rerank-Modell',
    },
    invalidVariable: 'Ungültige Variable',
  },
  singleRun: {
    testRun: 'Testlauf',
    startRun: 'Lauf starten',
    running: 'Läuft',
  },
  tabs: {
    'searchBlock': 'Suchblock',
    'blocks': 'Blöcke',
    'builtInTool': 'Integriertes Werkzeug',
    'customTool': 'Benutzerdefiniertes Werkzeug',
    'question-understand': 'Fragenverständnis',
    'logic': 'Logik',
    'transform': 'Transformieren',
    'utilities': 'Dienstprogramme',
    'noResult': 'Keine Übereinstimmung gefunden',
  },
  blocks: {
    'start': 'Start',
    'end': 'Ende',
    'answer': 'Antwort',
    'llm': 'LLM',
    'knowledge-retrieval': 'Wissensabruf',
    'question-classifier': 'Fragenklassifizierer',
    'if-else': 'IF/ELSE',
    'code': 'Code',
    'template-transform': 'Vorlage',
    'http-request': 'HTTP-Anfrage',
    'variable-assigner': 'Variablenzuweiser',
  },
  blocksAbout: {
    'start': 'Definieren der Startparameter zum Starten eines Workflows',
    'end': 'Definieren des Endes und des Ergebnistyps eines Workflows',
    'answer': 'Definieren des Antwortinhalts eines Chat-Gesprächs',
    'llm': 'Aufrufen von großen Sprachmodellen, um Fragen zu beantworten oder natürliche Sprache zu verarbeiten',
    'knowledge-retrieval': 'Ermöglicht das Abfragen von Textinhalten in Bezug auf Benutzerfragen aus dem Wissen',
    'question-classifier': 'Definieren der Klassifizierungsbedingungen von Benutzerfragen, LLM kann basierend auf der Klassifizierungsbeschreibung festlegen, wie das Gespräch fortschreitet',
    'if-else': 'Ermöglicht das Aufteilen des Workflows in zwei Zweige basierend auf if/else-Bedingungen',
    'code': 'Ausführen eines Stücks Python- oder NodeJS-Code, um benutzerdefinierte Logik zu implementieren',
    'template-transform': 'Daten mithilfe der Jinja-Vorlagensyntax in einen String konvertieren',
    'http-request': 'Ermöglicht das Senden von Serveranfragen über das HTTP-Protokoll',
    'variable-assigner': 'Variablen in verschiedenen Zweigen derselben Variable zuweisen, um eine einheitliche Konfiguration von Nachknoten zu erreichen',
  },
  operator: {
    zoomIn: 'Vergrößern',
    zoomOut: 'Verkleinern',
    zoomTo50: 'Auf 50% zoomen',
    zoomTo100: 'Auf 100% zoomen',
    zoomToFit: 'An Fenstergröße anpassen',
  },
  panel: {
    userInputField: 'Benutzereingabefeld',
    changeBlock: 'Block ändern',
    helpLink: 'Hilfe-Link',
    about: 'Über',
    createdBy: 'Erstellt von',
    nextStep: 'Nächster Schritt',
    addNextStep: 'Fügen Sie den nächsten Block in diesem Workflow hinzu',
    selectNextStep: 'Nächsten Block wählen',
    runThisStep: 'Diesen Schritt ausführen',
    checklist: 'Checkliste',
    checklistTip: 'Stellen Sie sicher, dass alle Probleme gelöst sind, bevor Sie veröffentlichen',
    checklistResolved: 'Alle Probleme gelöst',
    organizeBlocks: 'Blöcke organisieren',
    change: 'Ändern',
  },
  nodes: {
    common: {
      outputVars: 'Ausgabevariablen',
      insertVarTip: 'Variable einfügen',
      memory: {
        memory: 'Speicher',
        memoryTip: 'Chat-Speichereinstellungen',
        windowSize: 'Fenstergröße',
        conversationRoleName: 'Gesprächsrollenname',
        user: 'Benutzerprefix',
        assistant: 'Assistentenprefix',
      },
      memories: {
        title: 'Erinnerungen',
        tip: 'Chat-Speicher',
        builtIn: 'Eingebaut',
      },
    },
    start: {
      required: 'erforderlich',
      inputField: 'Eingabefeld',
      builtInVar: 'Eingebaute Variablen',
      outputVars: {
        query: 'Benutzereingabe',
        memories: {
          des: 'Gesprächsverlauf',
          type: 'Nachrichtentyp',
          content: 'Nachrichteninhalt',
        },
        files: 'Dateiliste',
      },
      noVarTip: 'Legen Sie Eingaben fest, die im Workflow verwendet werden können',
    },
    end: {
      outputs: 'Ausgaben',
      output: {
        type: 'Ausgabetyp',
        variable: 'Ausgabevariable',
      },
      type: {
        'none': 'Keine',
        'plain-text': 'Klartext',
        'structured': 'Strukturiert',
      },
    },
    answer: {
      answer: 'Antwort',
      outputVars: 'Ausgabevariablen',
    },
    llm: {
      model: 'Modell',
      variables: 'Variablen',
      context: 'Kontext',
      contextTooltip: 'Sie können Wissen als Kontext importieren',
      notSetContextInPromptTip: 'Um die Kontextfunktion zu aktivieren, füllen Sie bitte die Kontextvariable in PROMPT aus.',
      prompt: 'Aufforderung',
      roleDescription: {
        system: 'Geben Sie hochrangige Anweisungen für das Gespräch',
        user: 'Stellen Sie Anweisungen, Anfragen oder jegliche textbasierte Eingabe für das Modell bereit',
        assistant: 'Die Antworten des Modells basierend auf den Benutzernachrichten',
      },
      addMessage: 'Nachricht hinzufügen',
      vision: 'Vision',
      files: 'Dateien',
      resolution: {
        name: 'Auflösung',
        high: 'Hoch',
        low: 'Niedrig',
      },
      outputVars: {
        output: 'Inhalt generieren',
        usage: 'Modellnutzungsinformation',
      },
      singleRun: {
        variable: 'Variable',
      },
    },
    knowledgeRetrieval: {
      queryVariable: 'Abfragevariable',
      knowledge: 'Wissen',
      outputVars: {
        output: 'Abgerufene segmentierte Daten',
        content: 'Segmentierter Inhalt',
        title: 'Segmentierter Titel',
        icon: 'Segmentiertes Symbol',
        url: 'Segmentierte URL',
        metadata: 'Weitere Metadaten',
      },
    },
    http: {
      inputVars: 'Eingabevariablen',
      api: 'API',
      apiPlaceholder: 'Geben Sie die URL ein, tippen Sie ‘/’, um eine Variable einzufügen',
      notStartWithHttp: 'API sollte mit http:// oder https:// beginnen',
      key: 'Schlüssel',
      value: 'Wert',
      bulkEdit: 'Massenbearbeitung',
      keyValueEdit: 'Schlüssel-Wert-Bearbeitung',
      headers: 'Kopfzeilen',
      params: 'Parameter',
      body: 'Körper',
      outputVars: {
        body: 'Antwortinhalt',
        statusCode: 'Antwortstatuscode',
        headers: 'Antwortkopfzeilenliste JSON',
        files: 'Dateiliste',
      },
      authorization: {
        'authorization': 'Autorisierung',
        'authorizationType': 'Autorisierungstyp',
        'no-auth': 'Keine',
        'api-key': 'API-Schlüssel',
        'auth-type': 'Authentifizierungstyp',
        'basic': 'Basic',
        'bearer': 'Bearer',
        'custom': 'Benutzerdefiniert',
        'api-key-title': 'API-Schlüssel',
        'header': 'Kopfzeile',
      },
      insertVarPlaceholder: 'Tippen Sie ‘/’, um eine Variable einzufügen',
    },
    code: {
      inputVars: 'Eingabevariablen',
      outputVars: 'Ausgabevariablen',
    },
    templateTransform: {
      inputVars: 'Eingabevariablen',
      code: 'Code',
      codeSupportTip: 'Unterstützt nur Jinja2',
      outputVars: {
        output: 'Transformierter Inhalt',
      },
    },
    ifElse: {
      if: 'Wenn',
      else: 'Sonst',
      elseDescription: 'Wird verwendet, um die Logik zu definieren, die ausgeführt werden soll, wenn die Wenn-Bedingung nicht erfüllt ist.',
      and: 'und',
      or: 'oder',
      operator: 'Operator',
      notSetVariable: 'Bitte zuerst Variable festlegen',
      comparisonOperator: {
        'contains': 'enthält',
        'not contains': 'enthält nicht',
        'start with': 'beginnt mit',
        'end with': 'endet mit',
        'is': 'ist',
        'is not': 'ist nicht',
        'empty': 'ist leer',
        'not empty': 'ist nicht leer',
        'null': 'ist null',
        'not null': 'ist nicht null',
      },
      enterValue: 'Wert eingeben',
      addCondition: 'Bedingung hinzufügen',
      conditionNotSetup: 'Bedingung NICHT eingerichtet',
    },
    variableAssigner: {
      title: 'Variablen zuweisen',
      outputType: 'Ausgabetyp',
      outputVarType: 'Ausgabevariablentyp',
      varNotSet: 'Variable nicht gesetzt',
      noVarTip: 'Fügen Sie die zuzuweisenden Variablen hinzu',
      type: {
        string: 'Zeichenkette',
        number: 'Zahl',
        object: 'Objekt',
        array: 'Array',
      },
      outputVars: {
        output: 'Zugewiesener Variablenwert',
      },
    },
    tool: {
      toAuthorize: 'Zur Autorisierung',
      inputVars: 'Eingabevariablen',
      outputVars: {
        text: 'vom Werkzeug generierter Inhalt',
        files: {
          title: 'vom Werkzeug generierte Dateien',
          type: 'Unterstützter Typ. Aktuell nur Bild unterstützt',
          transfer_method: 'Übertragungsmethode. Wert ist remote_url oder local_file',
          url: 'Bild-URL',
          upload_file_id: 'Hochgeladene Datei-ID',
        },
      },
    },
    questionClassifiers: {
      model: 'Modell',
      inputVars: 'Eingabevariablen',
      class: 'Klasse',
      classNamePlaceholder: 'Schreiben Sie Ihren Klassennamen',
      advancedSetting: 'Erweiterte Einstellung',
      topicName: 'Themenname',
      topicPlaceholder: 'Schreiben Sie Ihren Themenname',
      addClass: 'Klasse hinzufügen',
      instruction: 'Anweisung',
      instructionPlaceholder: 'Schreiben Sie Ihre Anweisung',
    },
  },
  tracing: {
    stopBy: 'Angehalten von {{user}}',
  },
}

export default translation
