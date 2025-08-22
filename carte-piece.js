import {
  LitElement,
  html,
  css
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

const VERSION = "9.2.0";

console.info(
  `%c CARTE-PIECE %c ${VERSION} `,
  'color: white; background: #2c3e50; font-weight: 700;',
  'color: #2c3e50; background: white; font-weight: 700;',
);

const fireEvent = (node, type, detail, options) => {
  options = options || {};
  detail = detail === null || detail === undefined ? {} : detail;
  const event = new Event(type, {
    bubbles: options.bubbles === undefined ? true : options.bubbles,
    cancelable: Boolean(options.cancelable),
    composed: options.composed === undefined ? true : options.composed,
  });
  event.detail = detail;
  node.dispatchEvent(event);
  return event;
};

// --- EDITOR ---
class CartePieceEditor extends LitElement {
  static get properties() {
    return { hass: {}, _config: {} };
  }

  setConfig(config) {
    this._config = config || {};
  }

  _valueChanged(ev) {
    if (!this.hass) return;
    const { target } = ev;
    const newConfig = { ...this._config };
    const configValue = target.configValue;

    if (configValue) {
      let value = target.value;
      if (target.checked !== undefined) {
        value = target.checked;
      }

      if (value === '' || value === null || value === undefined) {
        delete newConfig[configValue];
      } else {
        newConfig[configValue] = value;
      }
    }

    fireEvent(this, "config-changed", { config: newConfig });
  }

  _renderButtonEditor(index) {
    const entityConfig = `button${index}_entity`;
    const nameConfig = `button${index}_name`;
    const showIconConfig = `button${index}_show_icon`;
    const showNameConfig = `button${index}_show_name`;
    const showStateConfig = `button${index}_show_state`;

    return html`
      <div class="button-editor-section">
        <h4>Bouton d'action ${index}</h4>
        <ha-entity-picker
          label="Entité"
          .hass=${this.hass}
          .value=${this._config[entityConfig] || ''}
          .configValue=${entityConfig}
          @value-changed=${this._valueChanged}
        ></ha-entity-picker>

        ${this._config[entityConfig] ? html`
          <ha-textfield
            label="Nom personnalisé (optionnel)"
            .value=${this._config[nameConfig] || ''}
            .configValue=${nameConfig}
            @input=${this._valueChanged}
            class="full-width"
          ></ha-textfield>
          <div class="side-by-side">
            <ha-formfield label="Icône">
              <ha-switch
                .checked=${this._config[showIconConfig] !== false}
                .configValue=${showIconConfig}
                @change=${this._valueChanged}
              ></ha-switch>
            </ha-formfield>
            <ha-formfield label="Nom">
              <ha-switch
                .checked=${this._config[showNameConfig] !== false}
                .configValue=${showNameConfig}
                @change=${this._valueChanged}
              ></ha-switch>
            </ha-formfield>
            <ha-formfield label="État">
              <ha-switch
                .checked=${this._config[showStateConfig] === true}
                .configValue=${showStateConfig}
                @change=${this._valueChanged}
              ></ha-switch>
            </ha-formfield>
          </div>
        ` : ''}
      </div>
    `;
  }

  _renderGeneralSettings() {
    return html`
      <details class="config-section" open>
        <summary>Général</summary>
        <div class="section-content">
          <ha-area-picker
            label="Zone de la pièce"
            .hass=${this.hass}
            .value="${this._config.area || ''}"
            .configValue=${"area"}
            @value-changed=${this._valueChanged}
          ></ha-area-picker>
          <ha-formfield label="Afficher les informations au-dessus de l'image ?">
            <ha-switch
              .checked=${this._config.info_above_image || false}
              .configValue=${"info_above_image"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
        </div>
      </details>
    `;
  }

  _renderSensorsSettings() {
    return html`
      <details class="config-section">
        <summary>Capteurs</summary>
        <div class="section-content">
          <ha-formfield label="Afficher la température ?">
            <ha-switch
              .checked=${this._config.show_temp || false}
              .configValue=${"show_temp"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
          ${this._config.show_temp ? html`
            <ha-entity-picker
              label="Capteur de température"
              .hass=${this.hass}
              .value="${this._config.temp_entity || ''}"
              .configValue=${"temp_entity"}
              @value-changed=${this._valueChanged}
              .includeDomains=${['sensor']}
            ></ha-entity-picker>
          ` : ''}

          <ha-formfield label="Afficher l'humidité ?">
            <ha-switch
              .checked=${this._config.show_humid || false}
              .configValue=${"show_humid"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
          ${this._config.show_humid ? html`
            <ha-entity-picker
              label="Capteur d'humidité"
              .hass=${this.hass}
              .value="${this._config.humid_entity || ''}"
              .configValue=${"humid_entity"}
              @value-changed=${this._valueChanged}
              .includeDomains=${['sensor']}
            ></ha-entity-picker>
          ` : ''}
        </div>
      </details>
    `;
  }

  _renderMediaSettings() {
    return html`
      <details class="config-section">
        <summary>Affichage Média</summary>
        <div class="section-content">
          <ha-select
            label="Type d'affichage"
            .value=${this._config.display_type || 'image'}
            .configValue=${"display_type"}
            @selected=${this._valueChanged}
            @closed=${(ev) => ev.stopPropagation()}
          >
            <mwc-list-item value="image">Image</mwc-list-item>
            <mwc-list-item value="compact">Compact (sans image)</mwc-list-item>
            <mwc-list-item value="video">Flux Vidéo</mwc-list-item>
            <mwc-list-item value="graph">Graphique Température</mwc-list-item>
          </ha-select>

          ${this._config.display_type === 'video' ? html`
            <ha-entity-picker
              label="Entité Caméra"
              .hass=${this.hass}
              .value="${this._config.camera_entity || ''}"
              .configValue=${"camera_entity"}
              @value-changed=${this._valueChanged}
              .includeDomains=${['camera']}
            ></ha-entity-picker>
          ` : ''}

          ${this._config.display_type === 'graph' && !this._config.temp_entity ? html`
              <ha-alert alert-type="warning">Veuillez sélectionner un capteur de température dans la section "Capteurs".</ha-alert>
          ` : ''}
        </div>
      </details>
    `;
  }

  _renderButtonsSettings() {
    const showActionButtons = this._config.show_action_buttons || false;
    return html`
      <details class="config-section">
        <summary>Boutons d'action</summary>
        <div class="section-content">
          <ha-formfield label="Activer les boutons d'action ?">
            <ha-switch
              .checked=${showActionButtons}
              .configValue=${"show_action_buttons"}
              @change=${this._valueChanged}
            ></ha-switch>
          </ha-formfield>
          ${showActionButtons ? html`
            ${[1, 2, 3, 4].map(i => this._renderButtonEditor(i))}
          ` : ''}
        </div>
      </details>
    `;
  }

  render() {
    if (!this.hass || !this._config) return html``;

    return html`
      <div class="card-config">
        ${this._renderGeneralSettings()}
        ${this._renderSensorsSettings()}
        ${this._renderMediaSettings()}
        ${this._renderButtonsSettings()}
      </div>
    `;
  }

  static get styles() {
    return css`
      .card-config {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .config-section {
        border: 1px solid var(--divider-color);
        border-radius: 8px;
      }
      details[open] > summary {
        border-bottom: 1px solid var(--divider-color);
      }
      summary {
        font-weight: bold;
        padding: 8px 12px;
        cursor: pointer;
        position: relative;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      summary::before {
        content: '►';
        display: inline-block;
        font-size: 0.8em;
        transition: transform 0.2s;
      }
      details[open] > summary::before {
        transform: rotate(90deg);
      }
      .section-content {
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 16px;
      }
      ha-alert {
        display: block;
      }
      .button-editor-section {
        border: 1px solid var(--divider-color);
        padding: 12px;
        border-radius: 6px;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      h4 {
        margin: 0 0 8px 0;
        font-size: 1.1em;
        font-weight: bold;
      }
      .side-by-side {
        display: flex;
        gap: 16px;
        align-items: center;
        flex-wrap: wrap;
      }
      .full-width {
        width: 100%;
      }
      ha-formfield {
        display: block;
        padding: 2px 0;
      }
    `;
  }
}
customElements.define('carte-piece-editor', CartePieceEditor);


// --- CARD ---
class CartePiece extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      _areaName: { state: true },
      _areaIcon: { state: true },
      _areaPicture: { state: true },
      _history: { state: true },
      _svgPath: { state: true },
    };
  }

  setConfig(config) {
    this.config = config;
    if (this.hass) {
      this._updateAreaData();
    }
  }

  set hass(hass) {
    this._hass = hass;
    this._updateAreaData();
  }

  updated(changedProperties) {
    super.updated(changedProperties);
    if (changedProperties.has('config')) {
        const oldConfig = changedProperties.get('config');
        const newConfig = this.config;

        if (newConfig.display_type === 'graph' && this.hass &&
            (!oldConfig || oldConfig.temp_entity !== newConfig.temp_entity)) {
            this._fetchHistory();
        }
    }
  }

  async _fetchHistory() {
    if (!this.hass || !this.config.temp_entity) return;
    this._svgPath = null;

    const endTime = new Date();
    const startTime = new Date();
    startTime.setHours(endTime.getHours() - 24);

    const url = `history/period/${startTime.toISOString()}?filter_entity_id=${this.config.temp_entity}&end_time=${endTime.toISOString()}&minimal_response`;

    try {
      const history = await this.hass.callApi('GET', url);
      if (history && history[0] && history[0].length > 1) {
        this._history = history[0];
        this._processHistory();
      } else {
        this._history = null;
      }
    } catch (err) {
      console.error("Error fetching history:", err);
      this._history = null;
    }
  }

  _processHistory() {
    if (!this._history) return;

    const data = this._history.map(item => ({
      time: new Date(item.last_changed).getTime(),
      state: parseFloat(item.state),
    })).filter(item => !isNaN(item.state));

    if (data.length < 2) return;

    const svgWidth = 500;
    const svgHeight = 100;

    const minTime = data[0].time;
    const maxTime = data[data.length - 1].time;
    const timeRange = maxTime - minTime;

    const states = data.map(item => item.state);
    const minState = Math.min(...states);
    const maxState = Math.max(...states);
    const stateRange = maxState - minState || 1;

    const points = data.map(item => {
      const x = ((item.time - minTime) / timeRange) * svgWidth;
      const y = svgHeight - ((item.state - minState) / stateRange) * svgHeight;
      return `${x},${y}`;
    });

    this._svgPath = "M" + points.join(" L");
  }

  _updateAreaData() {
    if (!this.config || !this._hass || !this.config.area) {
      this._areaName = 'Pièce';
      this._areaIcon = 'mdi:home';
      this._areaPicture = null;
      this.requestUpdate();
      return;
    }

    const areaId = this.config.area;
    const area = this._hass.areas[areaId];

    this._areaName = area ? area.name : 'Pièce';
    this._areaIcon = area ? area.icon || 'mdi:home' : 'mdi:home';
    this._areaPicture = area ? area.picture || null : null;

    this.requestUpdate();
  }

  getCardSize() {
    const displayType = this.config.display_type || 'image';
    if (displayType === 'compact') {
      return 1;
    }
    return 3;
  }

  _handleTap(entityId) {
    this._hass.callService("homeassistant", "toggle", {
      entity_id: entityId,
    });
  }

  _showMoreInfo(entityId) {
    const event = new Event("hass-more-info", {
      bubbles: true,
      composed: true,
    });
    event.detail = { entityId: entityId };
    this.dispatchEvent(event);
  }

  _renderMedia() {
    const displayType = this.config.display_type || 'image';

    switch (displayType) {
      case 'compact':
        return html``;

      case 'video':
        if (this.config.camera_entity) {
          return html`<hui-image
            .hass=${this._hass}
            .cameraImage=${this.config.camera_entity}
            .cameraView=${"live"}
          ></hui-image>`;
        }
        return html`<ha-alert alert-type="warning">Aucune entité caméra sélectionnée.</ha-alert>`;

      case 'graph':
        if (this.config.show_temp && this.config.temp_entity) {
          if (!this._svgPath) {
            return html`<div class="graph-placeholder">Chargement du graphique...</div>`;
          }
          return html`
            <svg viewBox="0 0 500 100" class="custom-graph-svg" preserveAspectRatio="none">
              <path d=${this._svgPath} fill="none" stroke="var(--primary-color)" stroke-width="5" />
            </svg>
          `;
        }
        return html`<ha-alert alert-type="warning">Aucun capteur de température sélectionné.</ha-alert>`;

      case 'image':
      default:
        if (this._areaPicture) {
          return html`<img class="room-image" src="${this._areaPicture}" alt="Image de la pièce" />`;
        }
        return html``;
    }
  }

  render() {
    if (!this.config || !this._hass) return html``;

    const infoAbove = this.config.info_above_image || false;
    const showButtons = this.config.show_action_buttons || false;
    const displayType = this.config.display_type || 'image';

    const showTemp = this.config.show_temp && this.config.temp_entity && this._hass.states[this.config.temp_entity];
    const showHumid = this.config.show_humid && this.config.humid_entity && this._hass.states[this.config.humid_entity];

    const tempStateObj = showTemp ? this._hass.states[this.config.temp_entity] : null;
    const humidStateObj = showHumid ? this._hass.states[this.config.humid_entity] : null;

    const tempState = tempStateObj ? `${tempStateObj.state}${tempStateObj.attributes.unit_of_measurement || ''}` : null;
    const humidState = humidStateObj ? `${humidStateObj.state}${humidStateObj.attributes.unit_of_measurement || ''}` : null;

    const content = html`
      <div class="info-grid">
        <ha-icon class="info-grid-icon" .icon=${this._areaIcon}></ha-icon>
        <span class="info-grid-name">${this._areaName}</span>
        <div class="info-grid-sensors">
          ${showTemp ? html`<span><ha-icon icon="mdi:thermometer"></ha-icon>${tempState}</span>` : ''}
          ${showHumid ? html`<span><ha-icon icon="mdi:water-percent"></ha-icon>${humidState}</span>` : ''}
        </div>
      </div>
    `;

    const buttons = [];
    if (showButtons && this._hass) {
      for (let i = 1; i <= 4; i++) {
        const entityId = this.config[`button${i}_entity`];
        if (entityId && this._hass.states[entityId]) {
          const stateObj = this._hass.states[entityId];

          const showIcon = this.config[`button${i}_show_icon`] !== false;
          const showName = this.config[`button${i}_show_name`] !== false;
          const showState = this.config[`button${i}_show_state`] === true;
          const customName = this.config[`button${i}_name`];
          const name = customName || stateObj.attributes.friendly_name;

          buttons.push(html`
            <div class="action-button" @click=${() => this._handleTap(entityId)} title="${name}">
              ${showIcon ? html`<ha-state-icon .stateObj=${stateObj} .stateColor=${true}></ha-state-icon>`: ''}
              ${showName || showState ? html`
                <div class="button-text">
                  ${showName ? html`<span class="button-name">${name}</span>` : ''}
                  ${showState ? html`<span class="button-state">${stateObj.state} ${stateObj.attributes.unit_of_measurement || ''}</span>` : ''}
                </div>
              ` : ''}
            </div>
          `);
        }
      }
    }

    const mediaContent = this._renderMedia();

    return html`
      <ha-card>
        <div class="content-wrapper">
          <div class="main-content">
            ${infoAbove ? html`${content}` : ''}
            ${mediaContent ? html`<div class="media-content media-content-${displayType}">${mediaContent}</div>` : ''}
            ${!infoAbove ? html`${content}` : ''}
          </div>
          ${buttons.length > 0 ? html`
            <div class="action-buttons">
              ${buttons}
            </div>
          ` : ''}
        </div>
      </ha-card>
    `;
  }

  static get styles() {
    return css`
      :host {
        display: flex;
        flex-direction: column;
        height: 100%;
        font-size: 12px; /* Set a base font size for the card */
      }
      ha-card {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 1em;
        box-sizing: border-box;
      }
      .content-wrapper {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        flex-grow: 1;
        gap: 1em;
      }
      .info-grid {
        display: grid;
        width: 100%;
        grid-template-areas:
          "i n"
          "i s";
        grid-template-columns: min-content 1fr;
        grid-template-rows: auto auto;
        gap: 0 0.8em;
        align-items: center;
        text-align: left;
      }
      .info-grid-icon {
        grid-area: i;
        --mdc-icon-size: 3em;
        color: var(--paper-item-icon-color, #44739e);
      }
      .info-grid-name {
        grid-area: n;
        font-size: 1.6em;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .info-grid-sensors {
        grid-area: s;
        display: flex;
        flex-wrap: wrap;
        gap: 1em;
        font-size: 1em;
        color: var(--secondary-text-color);
      }
      .info-grid-sensors span {
        display: flex;
        align-items: center;
        gap: 0.3em;
      }
      .info-grid-sensors ha-icon {
        --mdc-icon-size: 1.2em;
      }
      .media-content {
        width: 100%;
        height: auto;
        border-radius: 0.8em;
        overflow: hidden;
      }
      .media-content > * {
        width: 100%;
        height: 100%;
        display: block;
        object-fit: cover;
      }
      .custom-graph-svg {
        height: 150px; /* Keep a fixed height for the graph SVG container */
      }
      .graph-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 150px;
        background: rgba(0,0,0,0.05);
        border-radius: 0.8em;
        cursor: pointer;
        text-align: center;
        color: var(--primary-text-color);
        transition: background-color 0.2s;
      }
      .graph-placeholder:hover {
        background: rgba(0,0,0,0.1);
      }
      .graph-placeholder ha-icon {
        --mdc-icon-size: 3em;
      }
      .graph-placeholder .placeholder-text {
        margin-top: 0.5em;
        font-weight: 500;
      }
      .action-buttons {
        display: flex;
        justify-content: center;
        gap: 0.5em;
        width: 100%;
      }
      .action-button {
        flex: 1;
        min-width: 0; /* Allow shrinking */
        cursor: pointer;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 0.5em;
        box-sizing: border-box;
        padding: 0.8em;
        border-radius: 0.8em;
        border: 1px solid var(--divider-color);
        background: var(--card-background-color);
        transition: background-color 0.2s;
      }
      .action-button:hover {
        background: rgba(var(--rgb-primary-text-color), 0.05);
      }
      .action-button ha-state-icon {
        --mdc-icon-size: 1.8em;
      }
      .button-text {
        flex: 1;
        min-width: 0;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
      }
      .button-name, .button-state {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
      }
      .button-name {
        font-size: 1.1em;
        font-weight: bold;
        color: var(--primary-text-color);
      }
      .button-state {
        font-size: 1em;
        color: var(--secondary-text-color);
      }
    `;
  }

  static getConfigElement() {
    return document.createElement("carte-piece-editor");
  }
}
customElements.define('carte-piece', CartePiece);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "carte-piece",
  name: "Carte Pièce",
  preview: true,
  description: "Une carte personnalisée pour une pièce, avec auto-détection par zone.",
});
